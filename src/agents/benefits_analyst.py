"""Benefits Analyst - evaluates and suggests benefit adjustments."""

from src.agents.base import BaseAgent


class BenefitsAnalystAgent(BaseAgent):
    async def run(self, state: dict) -> dict:
        self.log_start(state)

        # For now, simple mock. In production: use RAG + LLM to analyse.
        current = ["401(k) matching", "Health insurance", "Paid time off"]
        recommended = ["Remote work stipend", "Mental health days", "Learning budget"]

        result = {
            "current_benefits_used": current,
            "recommended_benefits": recommended
        }
        self.log_end(result)
        return result
