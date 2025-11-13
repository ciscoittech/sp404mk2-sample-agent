"""
Routing pattern implementation.

Routes requests directly to specialized tools or agents based on triggers.
Most efficient pattern for well-defined tool mappings.
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass


@dataclass
class RoutingResult:
    """Result of routing execution."""
    success: bool
    result: Any
    route_taken: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RoutingPattern:
    """
    Routes requests to appropriate tools/agents.

    Simple and efficient pattern for direct tool mapping.
    """

    def __init__(self):
        """Initialize routing pattern."""
        self.routes: Dict[str, Callable] = {}

    def register_route(self, name: str, handler: Callable):
        """
        Register a route handler.

        Args:
            name: Route name (e.g., "youtube_search", "timestamp_extractor")
            handler: Async function to handle the route
        """
        self.routes[name] = handler

    async def execute(
        self,
        route_name: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingResult:
        """
        Execute routing to specified handler.

        Args:
            route_name: Name of route to execute
            user_input: User's input
            context: Optional context dict

        Returns:
            RoutingResult with execution details
        """
        context = context or {}

        if route_name not in self.routes:
            return RoutingResult(
                success=False,
                result=None,
                route_taken=route_name,
                error=f"Route '{route_name}' not found. Available: {list(self.routes.keys())}"
            )

        try:
            handler = self.routes[route_name]

            # Execute handler
            result = await handler(user_input, context)

            return RoutingResult(
                success=True,
                result=result,
                route_taken=route_name,
                metadata={"handler": route_name}
            )

        except Exception as e:
            return RoutingResult(
                success=False,
                result=None,
                route_taken=route_name,
                error=f"Route execution failed: {str(e)}"
            )

    def has_route(self, route_name: str) -> bool:
        """Check if a route exists."""
        return route_name in self.routes

    def list_routes(self) -> list:
        """List all registered routes."""
        return list(self.routes.keys())

    def __repr__(self) -> str:
        return f"RoutingPattern(routes={len(self.routes)})"
