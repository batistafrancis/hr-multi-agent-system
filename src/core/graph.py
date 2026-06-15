from langgraph.graph import StateGraph, END
from src.core.state import AgentState
from src.agents.researcher import ResearcherAgent
from src.agents.role_designer import RoleDesignerAgent
from src.agents.benefits_analyst import BenefitsAnalystAgent
from src.agents.report_compiler import ReportCompilerAgent


researcher = ResearcherAgent("researcher")
role_designer = RoleDesignerAgent("role_designer")
benefits_analyst = BenefitsAnalystAgent("benefits_analyst")
report_compiler = ReportCompilerAgent("report_compiler")


async def researcher_node(state: AgentState) -> dict:
    return await researcher.run(state) # type: ignore

async def role_designer_node(state: AgentState) -> dict:
    return await role_designer.run(state) # type: ignore

async def benefits_analyst_node(state: AgentState) -> dict:
    return await benefits_analyst.run(state) # type: ignore

async def report_compiler_node(state: AgentState) -> dict:
    return await report_compiler.run(state) #type: ignore


workflow = StateGraph(AgentState)
workflow.add_node("researcher", researcher_node)
workflow.add_node("role_designer", role_designer_node)
workflow.add_node("benefits_analyst", benefits_analyst_node)
workflow.add_node("report_compiler", report_compiler_node)
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "role_designer")
workflow.add_edge("role_designer", "benefits_analyst")
workflow.add_edge("benefits_analyst", "report_compiler")
workflow.add_edge("report_compiler", END)

graph = workflow.compile()
