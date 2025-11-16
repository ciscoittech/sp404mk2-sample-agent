"""
OpenRouter API Service for AI model integration.

Provides chat completion functionality with automatic cost tracking,
retry logic, and usage monitoring.
"""
import os
import asyncio
import logging
import httpx
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import tiktoken

from app.services.usage_tracking_service import UsageTrackingService
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterUsage(BaseModel):
    """Token usage statistics from OpenRouter API response."""
    prompt_tokens: int = Field(..., description="Number of tokens in the input prompt")
    completion_tokens: int = Field(..., description="Number of tokens in the generated completion")
    total_tokens: int = Field(..., description="Total tokens used (prompt + completion)")


class OpenRouterRequest(BaseModel):
    """Request model for OpenRouter chat completion."""
    model: str = Field(..., description="Model identifier (e.g., 'qwen/qwen3-7b-it')")
    messages: List[Dict[str, str]] = Field(..., description="List of message dicts with 'role' and 'content' keys")
    temperature: float = Field(default=0.5, description="Sampling temperature (0-2), controls randomness")
    max_tokens: int = Field(default=100, description="Maximum tokens to generate in the response")
    top_p: float = Field(default=1.0, description="Nucleus sampling parameter (0-1)")
    frequency_penalty: float = Field(default=0.0, description="Penalty for repeated tokens (-2 to 2)")
    presence_penalty: float = Field(default=0.0, description="Penalty for new tokens (-2 to 2)")


class OpenRouterResponse(BaseModel):
    """Response model from OpenRouter chat completion."""
    content: str = Field(..., description="Generated response text content")
    model: str = Field(..., description="Model that was used for generation")
    usage: OpenRouterUsage = Field(..., description="Token usage statistics")
    cost: float = Field(..., description="Total cost of the request in USD")
    request_id: Optional[str] = Field(default=None, description="Unique OpenRouter request ID")


class CostEstimate(BaseModel):
    """Cost estimate for a request before making the API call."""
    estimated_input_tokens: int = Field(..., description="Estimated number of input tokens")
    estimated_output_tokens: int = Field(..., description="Estimated number of output tokens")
    estimated_cost: float = Field(..., description="Estimated total cost in USD")
    model: str = Field(..., description="Model identifier for the estimate")


class OpenRouterError(Exception):
    """Custom exception for OpenRouter API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)


class OpenRouterService:
    """
    Service for interacting with OpenRouter API.

    Provides chat completion with automatic:
    - Cost tracking and database logging
    - Retry logic for transient failures
    - Token estimation and billing
    - Error handling and validation
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    # Model name aliases for backwards compatibility
    MODEL_ALIASES = {
        "qwen/qwen3-7b-it": "qwen/qwen-2.5-7b-instruct",  # Map to working 7B instruct model
    }

    def __init__(self, usage_tracking_service: UsageTrackingService):
        """
        Initialize OpenRouter service.

        Args:
            usage_tracking_service: Service for tracking API usage in database
        """
        self.usage_service = usage_tracking_service
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable must be set")

        self.app_url = settings.APP_URL

    def _resolve_model_name(self, model: str) -> str:
        """Resolve model aliases to actual model names."""
        return self.MODEL_ALIASES.get(model, model)

    async def chat_completion(self, request: OpenRouterRequest) -> OpenRouterResponse:
        """
        Execute a chat completion request with cost tracking.

        Makes API call to OpenRouter, parses response, calculates costs,
        and automatically logs usage to database.

        Args:
            request: Chat completion request parameters

        Returns:
            OpenRouterResponse with content, usage stats, and cost

        Raises:
            OpenRouterError: On API errors (auth, rate limit, etc.)
        """
        # Resolve model name (handle aliases)
        resolved_model = self._resolve_model_name(request.model)

        # Create request with resolved model name
        resolved_request = OpenRouterRequest(
            model=resolved_model,
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty
        )

        # Make API call with retry logic
        response_data = await self._make_request_with_retry(resolved_request)

        # Parse response (use original model name from request for consistency)
        response = self._parse_response(response_data, request.model)

        # Track usage in database
        await self._track_usage(
            model=response.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            cost=response.cost,
            request_id=response.request_id
        )

        return response

    async def estimate_cost(self, request: OpenRouterRequest) -> CostEstimate:
        """
        Estimate cost of a request without making API call.

        Args:
            request: The request to estimate costs for

        Returns:
            CostEstimate with token counts and estimated cost
        """
        # Estimate input tokens
        input_tokens = self._estimate_tokens(request.messages)
        output_tokens = request.max_tokens

        # Calculate cost
        pricing = settings.model_pricing.get(request.model, {"input": 0.0, "output": 0.0})
        if request.model not in settings.model_pricing:
            logger.warning(f"Model '{request.model}' not found in pricing table, using $0.00 fallback")
        input_cost = input_tokens * pricing["input"]
        output_cost = output_tokens * pricing["output"]
        total_cost = input_cost + output_cost

        return CostEstimate(
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            estimated_cost=total_cost,
            model=request.model
        )

    async def _make_request_with_retry(self, request: OpenRouterRequest) -> Dict[str, Any]:
        """
        Make HTTP request to OpenRouter with retry logic.

        Retries on transient failures (5xx errors), but not on:
        - Authentication errors (401)
        - Rate limits (429)
        - Invalid requests (400, 404)

        Args:
            request: The chat completion request

        Returns:
            Raw API response as dictionary

        Raises:
            OpenRouterError: On authentication or validation errors
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.app_url,
            "X-Title": "SP404MK2 Sample Agent",
            "Content-Type": "application/json"
        }

        payload = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty
        }

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.BASE_URL}/chat/completions",
                        json=payload,
                        headers=headers
                    )

                    # Handle authentication errors (don't retry)
                    if response.status_code == 401:
                        error_body = response.json() if response.text else {}
                        logger.error("Authentication failed: Invalid API key")
                        raise OpenRouterError(
                            message="Invalid API key or authentication failed",
                            status_code=401,
                            response_body=error_body
                        )

                    # Handle rate limiting (retry with exponential backoff)
                    if response.status_code == 429:
                        retry_count += 1
                        if retry_count >= max_retries:
                            error_body = response.json() if response.text else {}
                            logger.error(f"Rate limit exceeded after {max_retries} retries")
                            raise OpenRouterError(
                                message="Rate limit exceeded after retries",
                                status_code=429,
                                response_body=error_body
                            )
                        wait_time = min(2 ** retry_count, 10)
                        logger.warning(f"Rate limit hit, retrying after {wait_time}s (attempt {retry_count}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue

                    # Handle client errors (don't retry)
                    if 400 <= response.status_code < 500:
                        error_body = response.json() if response.text else {}
                        error_message = error_body.get("error", {}).get("message", f"Client error: {response.status_code}")
                        logger.error(f"Client error {response.status_code}: {error_message}")
                        raise OpenRouterError(
                            message=error_message,
                            status_code=response.status_code,
                            response_body=error_body
                        )

                    # Handle server errors (retry)
                    if response.status_code >= 500:
                        retry_count += 1
                        if retry_count >= max_retries:
                            error_body = response.json() if response.text else {}
                            logger.error(f"Server error {response.status_code} after {max_retries} retries")
                            raise OpenRouterError(
                                message=f"Server error after {max_retries} retries: {response.status_code}",
                                status_code=response.status_code,
                                response_body=error_body
                            )
                        wait_time = min(2 ** retry_count, 10)
                        logger.warning(f"Server error {response.status_code}, retrying after {wait_time}s (attempt {retry_count}/{max_retries})")
                        # Exponential backoff
                        await asyncio.sleep(wait_time)
                        continue

                    # Success
                    response.raise_for_status()
                    return response.json()

            except httpx.RequestError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Request failed after {max_retries} retries: {str(e)}")
                    raise OpenRouterError(
                        message=f"Request failed after {max_retries} retries: {str(e)}",
                        status_code=None,
                        response_body=None
                    )
                wait_time = min(2 ** retry_count, 10)
                logger.warning(f"Request error, retrying after {wait_time}s (attempt {retry_count}/{max_retries}): {str(e)}")
                # Exponential backoff
                await asyncio.sleep(wait_time)

    def _parse_response(self, response_data: Dict[str, Any], model: str) -> OpenRouterResponse:
        """
        Parse OpenRouter API response into structured model.

        Args:
            response_data: Raw API response dictionary
            model: Model name from request

        Returns:
            OpenRouterResponse with parsed data
        """
        # Extract content from first choice
        content = response_data["choices"][0]["message"]["content"] or ""

        # Extract usage statistics
        usage_data = response_data["usage"]
        usage = OpenRouterUsage(
            prompt_tokens=usage_data["prompt_tokens"],
            completion_tokens=usage_data["completion_tokens"],
            total_tokens=usage_data["total_tokens"]
        )

        # Calculate cost
        pricing = settings.model_pricing.get(model, {"input": 0.0, "output": 0.0})
        if model not in settings.model_pricing:
            logger.warning(f"Model '{model}' not found in pricing table, using $0.00 fallback")
        input_cost = usage.prompt_tokens * pricing["input"]
        output_cost = usage.completion_tokens * pricing["output"]
        total_cost = input_cost + output_cost

        # Extract request ID if available
        request_id = response_data.get("id")

        return OpenRouterResponse(
            content=content,
            model=model,
            usage=usage,
            cost=total_cost,
            request_id=request_id
        )

    async def _track_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        request_id: Optional[str] = None
    ) -> None:
        """
        Log API usage to database via UsageTrackingService.

        Args:
            model: Model name used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost: Total cost in USD
            request_id: Optional OpenRouter request ID
        """
        await self.usage_service.track_api_call(
            model=model,
            operation="chat_completion",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            extra_metadata={"request_id": request_id} if request_id else {}
        )

    def _estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Estimate token count for messages using tiktoken.

        Uses cl100k_base encoding (GPT-4 compatible) as approximation.

        Args:
            messages: List of message dictionaries with role and content

        Returns:
            Estimated token count
        """
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # Fallback to simple word count if tiktoken fails
            total_chars = sum(len(msg.get("content", "")) for msg in messages)
            return total_chars // 4  # Rough approximation

        total_tokens = 0
        for message in messages:
            # Count tokens in message content
            content = message.get("content", "")
            total_tokens += len(encoding.encode(content))
            # Add overhead for message formatting (role, etc.)
            total_tokens += 4

        # Add overhead for chat formatting
        total_tokens += 3

        return total_tokens
