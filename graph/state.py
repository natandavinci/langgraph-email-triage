from typing import TypedDict, Optional, List
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    """
    Representa o estado estruturado que flui por todos os nós do LangGraph.
    """
    sender_email: str
    body_email: str
    destination_sector: Optional[str]
    urgency: Optional[str]
    sentiment: Optional[str]
    account_level: Optional[str]
    final_answer: Optional[str]
    history: List[BaseMessage]