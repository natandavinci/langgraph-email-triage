import os
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage

# Importações da nossa nova estrutura profissional
from graph.state import GraphState
from agents.finance_agent import FinanceAgent

print("🧪 [DEBUG POO]: Inicializando teste do Agente Financeiro...")

# 1. Instanciamos a classe do nosso agente
agente_financeiro = FinanceAgent()

# 2. Criamos um mini-grafo temporário apenas para testar o nó do financeiro
workflow = StateGraph(GraphState)

# Passamos o método .answer da nossa classe como o nó do grafo!
workflow.add_node("finance_node", agente_financeiro.answer)

workflow.set_entry_point("finance_node")
workflow.add_edge("finance_node", END)

# 3. Inicializamos a memória em disco rígido (SQLite)
with SqliteSaver.from_conn_string("memoria_teste_poo.db") as memory:
    app = workflow.compile(checkpointer=memory)
    
    # ID de conversa fixo para testar se ele vai ler a base de dados reais (finance_policy.md)
    config = {"configurable": {"thread_id": "th_rodrigo_poo"}}

    # ==========================================
    # 📩 RODADA 1: Testando a injeção do manual de dados reais
    # ==========================================
    print("\n--- 📥 ENTRADA: E-mail sobre Cobrança Duplicada ---")
    inputs = {
        "sender_email": "rodrigo@email.com",
        "body_email": "Olá, fui cobrado duas vezes no meu cartão pelo último pagamento. Quero meu estorno.",
        "destination_sector": "Finance",
        "urgency": "High",
        "sentiment": "Angry",
        "account_level": "Free",
        "final_answer": None,
        "history": []
    }
    
    resultado = app.invoke(inputs, config=config)
    print("\n🤖 [RESPOSTA DA IA]:")
    print(resultado.get("final_answer"))