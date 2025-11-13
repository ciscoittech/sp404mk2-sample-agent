"""
Prompt chain pattern implementation.

Executes tasks sequentially with validation gates between steps.
Used for workflows where later steps depend on earlier results.
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum


class StepStatus(Enum):
    """Status of a chain step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ChainStep:
    """A single step in the prompt chain."""
    name: str
    handler: Callable
    description: str = ""
    gate: Optional[Callable] = None  # Validation function
    required: bool = True
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    error: Optional[str] = None


@dataclass
class ChainResult:
    """Result of prompt chain execution."""
    success: bool
    steps_completed: int
    steps_total: int
    results: Dict[str, Any] = field(default_factory=dict)
    errors: Dict[str, str] = field(default_factory=dict)
    final_result: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PromptChainPattern:
    """
    Sequential execution with validation gates.

    Features:
    - Ordered step execution
    - Validation gates between steps
    - Error handling and recovery
    - Step dependencies
    """

    def __init__(self):
        """Initialize prompt chain pattern."""
        self.steps: List[ChainStep] = []

    def add_step(
        self,
        name: str,
        handler: Callable,
        description: str = "",
        gate: Optional[Callable] = None,
        required: bool = True
    ) -> "PromptChainPattern":
        """
        Add a step to the chain.

        Args:
            name: Step name
            handler: Async function to execute
            description: Step description
            gate: Optional validation function (returns bool)
            required: If False, step can be skipped on failure

        Returns:
            Self for chaining
        """
        step = ChainStep(
            name=name,
            handler=handler,
            description=description,
            gate=gate,
            required=required
        )
        self.steps.append(step)
        return self

    async def execute(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ChainResult:
        """
        Execute the prompt chain.

        Args:
            user_input: User's input
            context: Optional context dict

        Returns:
            ChainResult with execution details
        """
        context = context or {}
        results = {}
        errors = {}
        steps_completed = 0

        for step in self.steps:
            step.status = StepStatus.RUNNING

            try:
                # Execute step handler
                step_result = await step.handler(user_input, context, results)

                # Run validation gate if present
                if step.gate:
                    gate_passed = await step.gate(step_result, context)

                    if not gate_passed:
                        error_msg = f"Validation gate failed for step '{step.name}'"

                        if step.required:
                            step.status = StepStatus.FAILED
                            step.error = error_msg
                            errors[step.name] = error_msg

                            return ChainResult(
                                success=False,
                                steps_completed=steps_completed,
                                steps_total=len(self.steps),
                                results=results,
                                errors=errors,
                                metadata={"failed_at": step.name}
                            )
                        else:
                            # Skip non-required step
                            step.status = StepStatus.SKIPPED
                            step.error = error_msg
                            errors[step.name] = error_msg
                            continue

                # Step successful
                step.status = StepStatus.COMPLETED
                step.result = step_result
                results[step.name] = step_result
                steps_completed += 1

            except Exception as e:
                error_msg = f"Step execution failed: {str(e)}"
                step.status = StepStatus.FAILED
                step.error = error_msg
                errors[step.name] = error_msg

                if step.required:
                    return ChainResult(
                        success=False,
                        steps_completed=steps_completed,
                        steps_total=len(self.steps),
                        results=results,
                        errors=errors,
                        metadata={"failed_at": step.name, "exception": str(e)}
                    )
                else:
                    # Continue if step not required
                    step.status = StepStatus.SKIPPED
                    continue

        # All steps completed
        final_result = results.get(self.steps[-1].name) if self.steps else None

        return ChainResult(
            success=True,
            steps_completed=steps_completed,
            steps_total=len(self.steps),
            results=results,
            errors=errors,
            final_result=final_result,
            metadata={"all_steps_completed": True}
        )

    def get_step_status(self) -> List[Dict[str, Any]]:
        """Get status of all steps."""
        return [
            {
                "name": step.name,
                "description": step.description,
                "status": step.status.value,
                "required": step.required,
                "error": step.error
            }
            for step in self.steps
        ]

    def reset(self):
        """Reset all steps to pending."""
        for step in self.steps:
            step.status = StepStatus.PENDING
            step.result = None
            step.error = None

    def __repr__(self) -> str:
        return f"PromptChainPattern(steps={len(self.steps)})"
