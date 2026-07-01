from langchain_core.messages import HumanMessage, AIMessage
from agents.base_agent import BaseAgent
from config.llm import call_llm
from graph.state import GraphState

class FinanceAgent(BaseAgent):
    """Agente especialista em demandas financeiras."""

    def __init__(self):
        super().__init__("finance_policy.md")

    def answer(self, state:GraphState) -> dict:
        print("\n💰 [NÓ POO: FINANCEIRO]: Processando resposta estratégica...")

        politica_real = self._load_policy()
        texto_historico = self._format_history(state.get("history",[]))

        # Regras dinâmicas baseadas na triagem
        alerta_prioridade = "🚨 PRIORIDADE MÁXIMA: Cliente com fúria ou urgência crítica. Seja extremamente formal, peça desculpas pelo transtorno e dê garantias." if state.get("sentiment") == "Angry" or state.get("urgency") == "Critical" else ""
        tratamento_vip = "⭐ CLIENTE VIP: Adicione ao final da assinatura o carimbo 'Atendimento Premium Neytans'." if state.get("account_level") == "VIP" else ""

        prompt = f"""
        You are Natanzinho_Finance, a customer support finance specialist for Neytans.
        Your task is to generate the next response that should be sent to the customer.

        # Operational Guidelines & Real Data (Follow strictly)
        {politica_real}

        {alerta_prioridade}
        {tratamento_vip}

        # Instructions
        - Always respond in the same language used by the customer.
        - Be professional, friendly and concise.
        - Return only the message that should be sent to the customer.
        - Do not explain your reasoning, do not use markdown, and do not use headings.

        # Interactions History (Past Conversations)
        {texto_historico}

        # Context Data
        Sender email: {state.get("sender_email")}
        Account Level: {state.get("account_level")}
        Customer Sentiment: {state.get("sentiment")}
        Urgency Level: {state.get("urgency")}

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