import os
from langchain_core.messages import HumanMessage
from config.llm import call_llm

class BaseAgent:
    """
    Classe base para todos os agentes do sistema.
    Centraliza a leitura de políticas e a formatação do histórico de conversas.
    """

    def __init(self, policy_filename: str):
        self.policy_path = os.path.join("data", policy_filename)

    def _load_policy(self) -> str:
        """Lê o arquivo de diretrizes e dados reais do agente."""
        if not os.path.exists(self.policy_path):
            return "Nenhuma diretriz específica para este setor."
        
        with open(self.policy_path, "r", encoding="utf-8") as f:
            return f.read()
        
    def _format_history(self, history: list) -> str:
        """Transforma a lista de objetos de mensagem do LangGraph em texto para o prompt."""
        if not history:
            return "Nenhuma interação anterior."
        
        texto_historico = ""
        for msg in history:
            origem = "Cliente" if isinstance(msg, HumanMessage) else "Suporte"
            texto_historico += f"{origem}: {msg.content}\n"
        return texto_historico