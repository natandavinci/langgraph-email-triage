import sys
from langgraph.checkpoint.sqlite import SqliteSaver

# Importando as configurações e o gerador do workflow
from config.settings import DB_CONNECTION_STRING
from graph.workflow import create_email_workflow

def process_inbound_emails():
    print("\n🚀 [SISTEMA NEYTANS]: Inicializando motor de execução de agentes...")
    
    # Busca a estrutura do grafo desenhada no workflow.py
    workflow = create_email_workflow()
    
    # Inicializa o Checkpointer com gerenciamento de contexto (Consertando o erro inicial!)
    with SqliteSaver.from_conn_string(DB_CONNECTION_STRING) as memory:
        app = workflow.compile(checkpointer=memory)
        print("💾 [MEMÓRIA]: Conectado ao banco de persistência local.")
        
        # ID de sessão persistente para simular o cliente
        config = {"configurable": {"thread_id": "cliente_rodrigo_producao"}}
        
        # E-mail de teste real que passará por todo o pipeline automaticamente!
        email_entrada = {
            "sender_email": "rodrigo_tech_enterprise@company.com",
            "body_email": "Precisamos de suporte urgente. Nosso dashboard de faturamento travou e os clientes estão reclamando. Consigo agendar um call com vocês?",
            "destination_sector": None,
            "urgency": None,
            "sentiment": None,
            "account_level": None,
            "final_answer": None,
            "history": []
        }
        
        # Executa o grafo inteiro de ponta a ponta
        print("\n📬 [E-MAIL RECEBIDO]: Iniciando processamento automático no Grafo...")
        estado_final = app.invoke(email_entrada, config=config)
        
        print("\n==================================================")
        print("🎯 EXECUÇÃO FINALIZADA COM SUCESSO")
        print("==================================================")
        print(f"👤 Remetente: {estado_final.get('sender_email')}")
        print(f"📊 Classificação de Conta: {estado_final.get('account_level')}")
        print(f"📈 Destino Determinado: {estado_final.get('destination_sector')}")
        print(f"🔥 Nível de Urgência: {estado_final.get('urgency')}")
        print("\n📧 [RESPOSTA FINAL ENVIADA AO CLIENTE]:")
        print(estado_final.get("final_answer"))

if __name__ == "__main__":
    process_inbound_emails()