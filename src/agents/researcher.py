"""Researcher agent - fetches market trends, competitor roles, compensation."""

from src.agents.base import BaseAgent
from src.tools.search import tavily_search


class ResearcherAgent(BaseAgent):
    async def run(self, state: dict) -> dict:
        self.log_start(state)
        topic = state["topic"]

        # Market trends
        trends = await tavily_search(f"Latest HR trends for {topic} 2025")

        # Competitor roles
        comp_roles = await tavily_search(f"Job description for {topic} at top companies")

        # Compensation data
        compensation = await tavily_search(f"Salary range for {topic} in tech industry")

        result = {
            "research_notes": trends,
            "competitor_roles": comp_roles,
            "compensation_data": {"summary": compensation[0] if compensation else "N/A"}
        }
        self.log_end(result)
        return result
