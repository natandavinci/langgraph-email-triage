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

    graph.add_node("triage_node", router.triage)
    graph.add_node("finance_node", finance.answer)
    graph.add_node("support_node", support.answer)
    graph.add_node("commercial_node", commercial.answer)
    graph.add_node("fallback_node", fallback.answer)

    graph.add_edge(START, "triage_node")

    graph.add_conditional_edges(
        "triage_node",
        router.route_decision,
        {
            "finance_node": "finance_node",
            "support_node": "support_node",
            "commercial_node": "commercial_node",
            "fallback_node": "fallback_node"
        }
    )

    graph.add_edge("finance_node", END)
    graph.add_edge("support_node", END)
    graph.add_edge("commercial_node", END)
    graph.add_edge("fallback_node", END)

    return graph