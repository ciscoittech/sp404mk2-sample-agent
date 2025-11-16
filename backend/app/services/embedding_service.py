"""
Embedding Service for generating text embeddings via OpenRouter API.

Provides text-to-vector embedding generation using OpenAI's text-embedding-3-small model
through OpenRouter. Includes batch processing, error handling, and cost tracking.
"""
import asyncio
import logging
from typing import List, Optional
import httpx

from app.services.usage_tracking_service import UsageTrackingService
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """Custom exception for embedding service errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class EmbeddingService:
    """
    Service for generating text embeddings using OpenRouter API.

    Uses OpenAI's text-embedding-3-small model (1536 dimensions) for generating
    vector representations of text. Excellent value and high quality embeddings.
    Includes automatic cost tracking and retry logic.
    """

    BASE_URL = "https://openrouter.ai/api/v1"
    MODEL = "openai/text-embedding-3-small"
    DIMENSIONS = 1536

    def __init__(self, usage_tracking_service: UsageTrackingService):
        """
        Initialize embedding service.

        Args:
            usage_tracking_service: Service for tracking API usage in database
        """
        self.usage_service = usage_tracking_service
        self.api_key = settings.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable must be set")

        self.app_url = settings.APP_URL

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text input.

        Args:
            text: Input text to embed (max ~8000 tokens)

        Returns:
            List of 768 floating point values representing the embedding

        Raises:
            EmbeddingError: On API errors or validation failures
        """
        if not text or not text.strip():
            raise EmbeddingError("Input text cannot be empty")

        # Make API call with retry logic
        response_data = await self._make_request_with_retry([text])

        # Extract embedding from response
        embedding = response_data["data"][0]["embedding"]

        # Track usage
        usage = response_data.get("usage", {})
        await self._track_usage(
            input_tokens=usage.get("prompt_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            num_texts=1
        )

        return embedding

    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call.

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors, one per input text

        Raises:
            EmbeddingError: On API errors or validation failures
        """
        if not texts:
            raise EmbeddingError("Input texts list cannot be empty")

        # Filter out empty strings
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise EmbeddingError("All input texts are empty")

        # Make API call with retry logic
        response_data = await self._make_request_with_retry(valid_texts)

        # Extract embeddings from response (sorted by index)
        embeddings_data = sorted(response_data["data"], key=lambda x: x["index"])
        embeddings = [item["embedding"] for item in embeddings_data]

        # Track usage
        usage = response_data.get("usage", {})
        await self._track_usage(
            input_tokens=usage.get("prompt_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            num_texts=len(valid_texts)
        )

        return embeddings

    async def _make_request_with_retry(self, inputs: List[str]) -> dict:
        """
        Make HTTP request to OpenRouter embeddings endpoint with retry logic.

        Args:
            inputs: List of text strings to embed

        Returns:
            Raw API response as dictionary

        Raises:
            EmbeddingError: On authentication or validation errors
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.app_url,
            "X-Title": "SP404MK2 Sample Agent",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.MODEL,
            "input": inputs
        }

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{self.BASE_URL}/embeddings",
                        json=payload,
                        headers=headers
                    )

                    # Handle authentication errors (don't retry)
                    if response.status_code == 401:
                        logger.error("Authentication failed: Invalid API key")
                        raise EmbeddingError(
                            message="Invalid API key or authentication failed",
                            status_code=401
                        )

                    # Handle rate limiting (retry with exponential backoff)
                    if response.status_code == 429:
                        retry_count += 1
                        if retry_count >= max_retries:
                            logger.error(f"Rate limit exceeded after {max_retries} retries")
                            raise EmbeddingError(
                                message="Rate limit exceeded after retries",
                                status_code=429
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
                        raise EmbeddingError(
                            message=error_message,
                            status_code=response.status_code
                        )

                    # Handle server errors (retry)
                    if response.status_code >= 500:
                        retry_count += 1
                        if retry_count >= max_retries:
                            logger.error(f"Server error {response.status_code} after {max_retries} retries")
                            raise EmbeddingError(
                                message=f"Server error after {max_retries} retries: {response.status_code}",
                                status_code=response.status_code
                            )
                        wait_time = min(2 ** retry_count, 10)
                        logger.warning(f"Server error {response.status_code}, retrying after {wait_time}s (attempt {retry_count}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue

                    # Success
                    response.raise_for_status()
                    return response.json()

            except httpx.RequestError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Request failed after {max_retries} retries: {str(e)}")
                    raise EmbeddingError(
                        message=f"Request failed after {max_retries} retries: {str(e)}"
                    )
                wait_time = min(2 ** retry_count, 10)
                logger.warning(f"Request error, retrying after {wait_time}s (attempt {retry_count}/{max_retries}): {str(e)}")
                await asyncio.sleep(wait_time)

    async def _track_usage(
        self,
        input_tokens: int,
        total_tokens: int,
        num_texts: int
    ) -> None:
        """
        Log API usage to database via UsageTrackingService.

        Args:
            input_tokens: Number of input tokens
            total_tokens: Total tokens used
            num_texts: Number of texts embedded
        """
        await self.usage_service.track_api_call(
            model=self.MODEL,
            operation="embedding_generation",
            input_tokens=input_tokens,
            output_tokens=0,  # Embeddings don't have output tokens
            extra_metadata={
                "num_texts": num_texts,
                "dimensions": self.DIMENSIONS
            }
        )
