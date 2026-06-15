from typing import TypedDict, List, Optional, Annotated
import operator


class AgentState(TypedDict):
    topic: str
    research_notes: Annotated[List[str], operator.add]
    competitor_roles: Annotated[List[str], operator.add]
    compensation_data: Optional[dict]
    drafted_role: Optional[dict]
    role_description: Optional[str]
    current_benefits_used: List[str]
    recommended_benefits: List[str]
    final_report: Optional[str]
    error: Optional[str]
