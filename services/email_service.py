import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.settings import EMAIL_ACCOUNT, EMAIL_PASSWORD, IMAP_SERVER, SMTP_SERVER, SMTP_PORT
from graph.state import GraphState

class EmailService:
    """
    Serviço de Infraestrutura para gerenciamento de leitura (IMAP) 
    e envio (SMTP) de e-mails integrados ao GraphState do ecossistema.
    """

    def __init__(self):
        self.user = EMAIL_ACCOUNT
        self.password = EMAIL_PASSWORD

        if not self.user or not self.password:
            print("⚠️ [AVISO EMAIL]: Credenciais de e-mail ausentes no arquivo .env")

    def fetch_unread_emails(self) -> list[dict]:
        """
        Conecta à caixa de entrada, busca e-mails não lidos,
        e converte cada um em um dicionário compatível com o GraphState.
        """
        emails_list = []
        try:
            # Conexão segura via IMAP
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(self.user, self.password)
            mail.select("inbox")

            # Busca por e-mails com a flag 'UNSEEN' (Não lidos)
            status, messages = mail.search(None, "UNSEEN")
            if status != "OK" or not messages[0]:
                return emails_list

            # Pega a lista de IDs de e-mails encontrados
            mail_ids = messages[0].split()
            print(f"📥 [EMAIL SERVICE]: Encontrado(s) {len(mail_ids)} e-mail(s) não lido(s).")

            # Vamos processar apenas o e-mail mais recente para o ciclo atual
            latest_id = mail_ids[-1]
            status, msg_data = mail.fetch(latest_id, "(RFC822)")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Transforma os bytes brutos em um objeto de mensagem legível
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Extrai o remetente
                    from_header = msg.get("From")
                    sender = from_header if from_header else "unknown@email.com"
                    
                    # Extrai o corpo do e-mail
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

                    # Estrutura o payload inicial compatível com o GraphState
                    email_payload = {
                        "sender_email": sender,
                        "body_email": body.strip(),
                        "destination_sector": None,
                        "urgency": None,
                        "sentiment": None,
                        "account_level": None,
                        "final_answer": None,
                        "history": []
                    }
                    emails_list.append(email_payload)
            
            mail.logout()
        except Exception as e:
            print(f"❌ [ERRO IMAP]: Falha ao ler caixa de entrada: {e}")
        
        return emails_list

    def send_response(self, state: GraphState) -> bool:
        """
        Consome a resposta final do estado gerado pelos agentes 
        e envia um e-mail de retorno para o cliente final.
        """
        destinatario = state.get("sender_email")
        mensagem_corpo = state.get("final_answer")

        if not destinatario or not mensagem_corpo:
            print("🚨 [ERRO SMTP]: Dados insuficientes no estado para realizar o envio.")
            return False

        try:
            print(f"📤 [EMAIL SERVICE]: Preparando envio de resposta para {destinatario}...")
            
            # Montagem estruturada da mensagem MIME
            msg = MIMEMultipart()
            msg["From"] = self.user
            msg["To"] = destinatario
            msg["Subject"] = f"RE: Atendimento Automatizado Neytans"

            msg.attach(MIMEText(mensagem_corpo, "plain", "utf-8"))

            # Conexão segura e autenticação via SMTP SSL
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(self.user, self.password)
                server.sendmail(self.user, destinatario, msg.as_string())
            
            print(f"✨ [EMAIL SERVICE]: E-mail enviado com sucesso para {destinatario}!")
            return True
        except Exception as e:
            print(f"❌ [ERRO SMTP]: Falha ao enviar e-mail: {e}")
            return False