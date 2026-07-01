import sys
import hashlib
from dotenv import load_dotenv
load_dotenv()
from langgraph.checkpoint.sqlite import SqliteSaver

# Importando as configurações, o gerador do workflow e o serviço de e-mail
from config.settings import DB_CONNECTION_STRING
from graph.workflow import create_email_workflow
from services.email_service import EmailService
from langchain_core.runnables.graph import MermaidDrawMethod

def process_inbound_emails():
    print("\n🚀 [SISTEMA NEYTANS]: Inicializando motor de execução de agentes...")
    
    # 1. Instancia o serviço de infraestrutura de e-mail
    email_service = EmailService()
    
    # 2. Busca e-mails não lidos reais diretamente da caixa postal (IMAP)
    emails_reais = email_service.fetch_unread_emails()
    
    if not emails_reais:
        print("📭 [FILA LIMPA]: Nenhum e-mail não lido encontrado na caixa postal. Encerrando execução.")
        return

    print(f"📥 [PRODUÇÃO]: Iniciando processamento do e-mail real recebido.")
    email_entrada = emails_reais[0]  # Pega o primeiro e-mail da fila de não lidos

    # 🔍 PRINT DE LOG PARA DEBUG: Mensagem do cliente capturada
    print("\n==================================================")
    print("👀 [DEBUG INBOUND]: DADOS DO CLIENTE CAPTURADOS")
    print("==================================================")
    print(f"De: {email_entrada.get('sender_email')}")
    print(f"Mensagem Bruta Recebida:\n{email_entrada.get('body_email')}")
    print("==================================================\n")
    
    # 3. Busca a estrutura do grafo desenhada no workflow.py
    workflow = create_email_workflow()
    
    # 4. Inicializa o Checkpointer com gerenciamento de contexto
    with SqliteSaver.from_conn_string(DB_CONNECTION_STRING) as memory:
        app = workflow.compile(checkpointer=memory)
        print("💾 [MEMÓRIA]: Conectado ao banco de persistência local.")
        
        try:
            png_bytes = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
            with open("grafo_exemplo1.png", "wb") as f:
                f.write(png_bytes)
            print("🖼️ [DOCUMENTAÇÃO]: Imagem do grafo gerada com sucesso em 'grafo_exemplo1.png'!")
        except Exception as e:
            print(f"⚠️ [AVISO GRAFO]: Não foi possível gerar a imagem do grafo. Erro: {e}")

        # Gera uma thread_id dinâmica baseada no remetente para manter o histórico isolado por cliente
        remetente = email_entrada.get("sender_email", "desconhecido")
        thread_hash = hashlib.md5(remetente.encode()).hexdigest()[:12]
        config = {"configurable": {"thread_id": f"thread_{thread_hash}"}}
        
        # 5. Executa o grafo inteiro de ponta a ponta
        print(f"\n📬 [GRAFO]: Processando payload através dos nós de IA (Thread: thread_{thread_hash})...")
        estado_final = app.invoke(email_entrada, config=config)
        
        print("\n==================================================")
        print("🎯 EXECUÇÃO FINALIZADA COM SUCESSO")
        print("==================================================")
        print(f"👤 Remetente: {estado_final.get('sender_email')}")
        print(f"📊 Classificação de Conta: {estado_final.get('account_level')}")
        print(f"📈 Destino Determinado: {estado_final.get('destination_sector')}")
        print(f"🔥 Nível de Urgência: {estado_final.get('urgency')}")
        print("\n📧 [RESPOSTA FINAL GERADA PELA IA]:")
        print(estado_final.get("final_answer"))
        
        # 6. Dispara o e-mail real de volta para a internet
        print("\n✉️ [OUTBOUND]: Enviando resposta para o servidor SMTP...")
        sucesso = email_service.send_response(estado_final)
        if sucesso:
            print("✨ [PROCESSO CONCLUÍDO]: Resposta real enviada com sucesso ao cliente!")
        else:
            print("❌ [AVISO]: O Grafo processou, mas houve uma falha técnica no envio do e-mail.")


if __name__ == "__main__":
    process_inbound_emails()