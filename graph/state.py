from typing import TypedDict, Optional, List,Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

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
    history: Annotated[list, add_messages]