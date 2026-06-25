from typing import Protocol, Any


class Evaluator(Protocol):
    async def evaluate(
        self,
        reference: dict[str, Any],
        actual: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Evaluate the actual output against the reference.
        Returns a flat dictionary containing scores or error tracking logs.
        """
        ...
