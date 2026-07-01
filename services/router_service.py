import json
from config.llm import call_llm
from graph.state import GraphState

class RouterService:
    """
    Serviço responsável por analisar o e-mail de entrada, enriquecer o contexto
    (sentimento, urgência, plano) e definir o setor de destino (roteamento).
    """
    def triage(self, state: GraphState) -> dict:
        print("\n🔍 [SERVIÇO: TRIAGEM & ROTEAMENTO]: Analisando metadados do e-mail...")
        
        prompt = f"""
        You are an elite inbound email router for Ardael.
        Analyze the following email and extract metadata for routing.

        # Input Email:
        "{state.get("body_email")}"

        # Sender Address:
        "{state.get("sender_email")}"

        # JSON Output Requirements:
        Return EXCLUSIVELY a valid JSON object matching these exact keys. Do not include markdown code blocks or wrapping.
        
        - "destination_sector": String. Choose exactly one of: "Support", "Finance", "Commercial", "Fallback".
        - "urgency": String. Choose exactly one of: "Low", "Medium", "High", "Critical".
        - "sentiment": String. Choose exactly one of: "Angry", "Anxious", "Neutral", "Happy".
        - "account_level": String. If the sender email ends with a corporate domain (not gmail/outlook/hotmail/yahoo) or contains keywords indicating top-tier business, class as "VIP", otherwise "Free".

        Example response:
        {{"destination_sector": "Support", "urgency": "High", "sentiment": "Anxious", "account_level": "VIP"}}
        """
        
        response_text = call_llm(prompt)
        
        # Limpeza de segurança caso a LLM insira marcações markdown
        response_clean = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            metadata = json.loads(response_clean)
            print(f"🎯 Triagem Concluída -> Setor: {metadata.get('destination_sector')} | Urgência: {metadata.get('urgency')} | Nível: {metadata.get('account_level')}")
            return metadata
        except Exception as e:
            print(f"🚨 [ERRO TRIAGEM]: Falha ao processar JSON da triagem. Ativando Fallback. Erro: {e}")
            return {
                "destination_sector": "Fallback",
                "urgency": "Medium",
                "sentiment": "Neutral",
                "account_level": "Free"
            }
        
    @staticmethod
    def route_decision(state: GraphState, *args, **kwargs) -> str:
        """
        Função de decisão condicional do LangGraph.
        O uso de *args e **kwargs garante compatibilidade com os parâmetros 
        internos de configuração que o LangGraph injeta na chamada.
        """
        sector = state.get("destination_sector")
        if sector == "Support":
            return "support_node"
        elif sector == "Finance":
            return "finance_node"
        elif sector == "Commercial":
            return "commercial_node"
        else:
            return "fallback_node"