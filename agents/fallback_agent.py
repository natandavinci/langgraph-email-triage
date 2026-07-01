from langchain_core.messages import HumanMessage, AIMessage
from agents.base_agent import BaseAgent
from config.llm import call_llm
from graph.state import GraphState

class FallbackAgent(BaseAgent):
    """Agente de contingência para roteamentos inválidos."""

    def __init__(self):
        super().__init__("")

    def answer(self, state: GraphState) -> dict:
        print("\n🚨 [NÓ POO: FALLBACK]: Setor inválido. Gerando resposta de segurança...")
        
        texto_historico = self._format_history(state.get("history", []))

        prompt = f"""
        You are Natanzinho_Specialist, a senior customer relations coordinator at Neytans.
        We had a minor internal routing delay with your ticket, so I am taking over personally.
        
        Write a very polite email to the customer stating that their request has been received 
        and a specialized human manager is reviewing it right now to give a precise answer within the next few hours.
        
        # Instructions
        - Respond in Portuguese.
        - Be extremely polite, professional, and reassuring.
        - Do not use markdown or headings.
        
        # Interactions History (Past Conversations)
        {texto_historico}
        
        # Customer Email
        "{state.get("body_email")}"
        """

        response_ia = call_llm(prompt)

        return {
            "final_answer": response_ia, 
            "destination_sector": "Human_Contigency",
            "history": [
                HumanMessage(content=state['body_email']),
                AIMessage(content=response_ia)
            ]
        }