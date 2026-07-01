from langchain_core.messages import HumanMessage, AIMessage
from agents.base_agent import BaseAgent
from config.llm import call_llm
from graph.state import GraphState

class SupportAgent(BaseAgent):
    """Agente especialista em suporte técnico e infraestrutura."""

    def __init__(self):
        super().__init__("support_policy.md")

    def answer(self, state: GraphState) -> dict:
        print("\n🛠️ [NÓ POO: SUPORTE]: Processando resposta técnica...")

        politica_real = self._load_policy
        texto_historico = self._format_history(state.get("history",[]))

        alerta_prioridade = "🚨 PRIORIDADE MÁXIMA: Falha crítica de sistema ou cliente irritado. Ofereça uma solução imediata ou escalonamento imediato para engenharia." if state.get("sentiment") == "Angry" or state.get("urgency") == "Critical" else ""
        tratamento_vip = "⭐ CLIENTE VIP: Ofereça a opção de agendar uma chamada de suporte dedicada de 15 minutos." if state.get("account_level") == "VIP" else ""

        prompt = f"""
        You are Natanzinho_Support, a customer support specialist for Neytans.
        Your task is to generate the next response that should be sent to the customer.

        # Operational Guidelines & Real Data (Follow strictly)
        {politica_real}

        {alerta_prioridade}
        {tratamento_vip}

        # Instructions
        - Always respond in Portuguese.
        - Be clear, objective, helpful and technical, yet highly polite.
        - Return only the message that should be sent to the customer.
        - Do not explain your reasoning, do not use markdown, and do not use headings.

        # Interactions History (Past Conversations)
        {texto_historico}

        # New Customer Email (Answer this one now)
        "{state.get("body_email")}"

        Generate the customer reply now in email form using this information.
        """

        response_ia = call_llm(prompt)

        return{
            "final_answer": response_ia,
            "history": [
                HumanMessage(content=state['body_email']),
                AIMessage(content=response_ia)
            ]
        }