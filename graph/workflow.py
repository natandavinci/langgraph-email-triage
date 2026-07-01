from langgraph.graph import StateGraph, START, END

from graph.state import GraphState
from services.router_service import RouterService
from agents.finance_agent import FinanceAgent
from agents.support_agent import SupportAgent
from agents.commercial_agent import CommercialAgent
from agents.fallback_agent import FallbackAgent

def create_email_workflow() -> StateGraph:
    """
    Instancia todos os serviços e agentes, monta e conecta a arquitetura do Grafo.
    """

    router = RouterService()
    finance = FinanceAgent()
    support = SupportAgent()
    commercial = CommercialAgent()
    fallback = FallbackAgent()

    graph  = StateGraph(GraphState)

    graph.add_node("triage", router.triage)
    graph.add_node("finance", finance.answer)
    graph.add_node("support", support.answer)
    graph.add_node("commercial", commercial.answer)
    graph.add_node("fallback", fallback.answer)

    graph.add_edge(START, "triage")

    graph.add_conditional_edges(
        "triage",
        router.route_decision,
        {
            "finance": "finance",
            "support": "support",
            "commercial": "commercial",
            "fallback": "fallback"
        }
    )

    graph.add_edge("finance", END)
    graph.add_edge("support", END)
    graph.add_edge("commercial", END)
    graph.add_edge("fallback", END)

    return graph