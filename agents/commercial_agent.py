from langchain_core.messages import HumanMessage, AIMessage
from agents.base_agent import BaseAgent
from config.llm import call_llm
from graph.state import GraphState

class CommercialAgent(BaseAgent):
    """Agente especialista em negociações e oportunidades comerciais."""

    def __init__(self):
        super().__init__("commercial_policy.md")

    def answer(self, state: GraphState) -> dict:
        print("\n🤝 [NÓ POO: COMERCIAL]: Processando retorno de negócios...")

        politica_real = self._load_policy()
        texto_historico = self._format_history(state.get("history", []))

        tratamento_vip = "⭐ LEAD VIP: Trate como potencial parceiro estratégico nível Gold. Use tom altamente persuasivo." if state.get("account_level") == "VIP" else ""

        prompt = f"""
        You are Natanzinho_Commercial, a customer support commercial specialist for Neytans.
        Your task is to generate the next response that should be sent to the customer.

        # Operational Guidelines & Real Data (Follow strictly)
        {politica_real}

        {tratamento_vip}

        # Instructions
        - Always respond in Portuguese.
        - Be professional, commercial, enthusiastic and concise.
        - Highlight our interest in evaluating solid opportunities.
        - Return only the message that should be sent to the customer.
        - Do not explain your reasoning, do not use markdown, and do not use headings.

        # Interactions History (Past Conversations)
        {texto_historico}

        # New Customer Email (Answer this one now)
        "{state.get("body_email")}"

        Generate the customer reply now in email form using this information.
        """

        response_ia = call_llm(prompt)

        return {
            "final_answer": response_ia,
            "history": [
                HumanMessage(content=state["body_email"]),
                AIMessage(content=response_ia)
            ]
        }