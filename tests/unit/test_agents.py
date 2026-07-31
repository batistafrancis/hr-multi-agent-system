import pytest
from src.agents.researcher import ResearcherAgent
from src.agents.role_designer import RoleDesignerAgent
from src.agents.benefits_analyst import BenefitsAnalystAgent
from src.agents.report_compiler import ReportCompilerAgent

@pytest.mark.asyncio
async def test_researcher_returns_note():
    agent = ResearcherAgent("test")
    state = {"topic": "AI Ethics Manager"}
    result = await agent.run(state)
    assert "research_notes" in result
    assert isinstance(result["research_notes"], list)

@pytest.mark.asyncio
async def test_role_designer_uses_state():
    agent = RoleDesignerAgent("test")
    state = {
        "topic": "AI Ethics Manager",
        "research_notes": ["Some research"]
    }
    result = await agent.run(state)
    assert "research_notes" in result
    assert "role_description" in result

@pytest.mark.asyncio
async def test_benefits_analyst_returns_lists():
    agent = BenefitsAnalystAgent("test")
    result = await agent.run({})
    assert "current_benefits_used" in result
    assert "recommended_benefits" in result
    assert isinstance(result["recommended_benefits"], list)

@pytest.mark.asyncio
async def test_report_compiler_returns_report():
    agent = ReportCompilerAgent("test")
    state = {
        "topic": "AI Ethics Manager",
        "research_notes": ["Trend: AI ethics growing"],
        "role_description": "A great role",
        "recommended_benefits": ["401k", "Health"]
    }
    result = await agent.run(state)
    assert "final_report" in result
    assert "AI Ethics Manager" in result["final_report"]
