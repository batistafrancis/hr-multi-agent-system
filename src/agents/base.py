"""Base agent with logging and tracing."""

from abc import ABC, abstractmethod
from typing import Any
from src.utils.logging_conf import get_logger


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(__name__)
        self.logger.info(f"Initialised agent: {name}")

    @abstractmethod
    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute agent logic and update state."""
        pass

    def log_start(self, state: dict[str, Any]):
        self.logger.info(f"[{self.name}] Starting", extra={"topic": state.get("topic")})

    def log_end(self, result: dict[str, Any]):
        self.logger.info(f"[{self.name}] Completed")
