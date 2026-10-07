import pytest
from src.core.graph import graph
from src.core.state import AgentState


@pytest.mark.asyncio
async def test_full_workflow(offline_providers):
    state: AgentState = {
        "topic": "Data Privacy Office",
        "research_notes": [],
        "competitor_roles": [],
        "compensation_data": None,
        "drafted_role": None,
        "role_description": None,
        "current_benefits_used": [],
        "recommended_benefits": [],
        "final_report": None,
        "error": None,
    }
    result = await graph.ainvoke(state)
    assert "final_report" in result
    assert "role_description" in result
    assert len(result["final_report"]) > 0
    assert len(result["role_description"]) > 0
    assert "Trend: AI ethics growing" in result["final_report"]
    assert "Mental health days" in result["final_report"]
