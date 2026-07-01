from typing import (
    Optional,
    Literal,
    Annotated
)
from typing_extensions import TypedDict
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import json
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.checkpoint.sqlite import SqliteSaver
import smtplib
import imaplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_core.messages import HumanMessage, AIMessage
import operator


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)

# State
class GraphState(TypedDict):

    sender_email: Optional[str]

    body_email: Optional[str]

    destination_sector: Optional[str]

    final_answer: Optional[str]

    sentiment: Optional[str]

    urgency: Optional[str]

    account_level: Optional[str]

    history: Annotated[list, add_messages]

class EmailClassification(BaseModel):
   
    sector: Literal["Finance", "Support", "Commercial"] = Field(
        description="O setor de destino com base no conteúdo do e-mail."
    )
    urgency: Literal["Low", "Medium", "High", "Critical"] = Field(
        description="O nível de urgência do e-mail. 'Critical' deve ser usado apenas para ameaças de processo, fúria extrema ou falhas totais de sistema."
    )
    sentiment: Literal["Angry", "Neutral", "Satisfied"] = Field(
        description="O estado emocional predominante do cliente no e-mail."
    )
# Node-1
def classify_email(state: GraphState) -> dict:

    body_email = state["body_email"]
    
    prompt = f"""
        Você é um Analista de Triagem de IA Avançado.
        Sua tarefa é analisar o e-mail abaixo e extrair o setor responsável, o nível de urgência e o sentimento do cliente.
        
        E-mail do Cliente:
        "{body_email}"
        """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(

            response_mime_type="application/json",
            response_schema=EmailClassification,
        )
    )
    
    extract_data = json.loads(response.text)
    print(f"📊 [TRIAGEM CONCLUÍDA]: Setor -> {extract_data['sector']} | Urgência -> {extract_data['urgency']} | Sentimento -> {extract_data['sentiment']}")

    return {"destination_sector": extract_data["sector"], "urgency": extract_data["urgency"], "sentiment": extract_data["sentiment"]}

#NeW NODE
def enrich_data(state:GraphState) -> dict:
    print("\n🗄️ [NÓ: ENRIQUECIMENTO]: Consultando banco de dados do cliente...")
    email_cliente = state["sender_email"]
   
   # Simulação de uma tabela no Banco de Dados (E-mails cadastrados como VIP)
    BANCO_DADOS_VIPS = [
        "cliente_vip@email.com",
        "rodrigo_premium@email.com",
        "parceiro_comercial@neytans.com"
    ]

    if email_cliente in BANCO_DADOS_VIPS:
        nivel = "VIP"

    else:
        nivel = "Free"

    print(f"💎 [DADOS ENRIQUECIDOS]: Cliente carimbado como nível: {nivel}")

    return {"account_level": nivel}

# New function
def answer_fallback(state: GraphState) -> dict:
    print("\n🚨 [NÓ: FALLBACK]: Setor inválido ou falha de triagem. Gerando resposta de segurança...")
    
    historico_mensagens = state.get("history") or []
    texto_historico = ""
    for msg in historico_mensagens:
        if isinstance(msg, HumanMessage):
            origem = "Cliente"
        else:
            origem = "Suporte"
        texto_historico += f"{origem}: {msg.content}\n"
    
    if not texto_historico:
        texto_historico = "Nenhuma interação anterior."

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
    "{state['body_email']}"
    """

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    response_ia = response.text

    return {
        "final_answer": response_ia, 
        "destination_sector": "Human_Contigency",
        "history": [
            HumanMessage(content=state['body_email']),
            AIMessage(content=response_ia)
        ]
    }


# Node-2
def answer_finance(state: GraphState) -> dict:
    print("\n💰 [NÓ: RESPOSTA FINANCEIRO]: Gerando resposta estratégica...")
    historico_mensagens = state.get("history") or []

    texto_historico = ""
    for msg in historico_mensagens:
        # 🚨 CORREÇÃO PROFISSIONAL: Verifica o tipo real da classe LangChain
        if isinstance(msg, HumanMessage):
            origem = "Cliente"
        else:
            origem = "Suporte"
            
        # Acessa o conteúdo do objeto usando .content (e não .get())
        texto_historico += f"{origem}: {msg.content}\n"
    
    if not texto_historico:
        texto_historico = "Nenhuma interação anterior."

    # Criamos regras dinâmicas de acordo com o estado do cliente
    alerta_prioridade = "🚨 PRIORIDADE MÁXIMA: Cliente com fúria ou urgência crítica. Seja extremamente formal, peça desculpas pelo transtorno e dê garantias." if state["sentiment"] == "Angry" or state["urgency"] == "Critical" else ""
    tratamento_vip = "⭐ CLIENTE VIP: Adicione ao final da assinatura o carimbo 'Atendimento Premium Neytans'." if state["account_level"] == "VIP" else ""

    prompt = f"""
    You are Natanzinho_Finance, a customer support finance specialist for Neytans.
    Your task is to generate the next response that should be sent to the customer.

    {alerta_prioridade}
    {tratamento_vip}

    # Instructions
    - Always respond in the same language used by the customer.
    - Be professional, friendly and concise.
    - Follow all procedures and guidelines provided.
    - Return only the message that should be sent to the customer.
    - Do not explain your reasoning, do not use markdown, and do not use headings.

    # Interactions History (Past Conversations)
    {texto_historico}

    # Context Data
    Sender email: {state["sender_email"]}
    Account Level: {state["account_level"]}
    Customer Sentiment: {state["sentiment"]}
    Urgency Level: {state["urgency"]}

    # New Customer Email (Answer this one now)
    "{state['body_email']}"

    Generate the customer reply now in email form using this information.
    """
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    response_ia = response.text

    # 🚨 RETORNO PADRÃO DE MERCADO: Devolvemos os objetos limpos na lista
    return {
        "final_answer": response_ia,
        "history": [
            HumanMessage(content=state['body_email']),
            AIMessage(content=response_ia)
        ]
    }



# Node-3
def answer_support(state: GraphState) -> dict:
    print("\n🛠️ [NÓ: RESPOSTA SUPORTE]: Gerando resposta técnica...")

    historico_mensagens = state.get("history") or []
    texto_historico = ""
    for msg in historico_mensagens:
        if isinstance(msg, HumanMessage):
            origem = "Cliente"
        else:
            origem = "Suporte"
        texto_historico += f"{origem}: {msg.content}\n"
    
    if not texto_historico:
        texto_historico = "Nenhuma interação anterior."
    
    alerta_prioridade = "🚨 PRIORIDADE MÁXIMA: Falha crítica de sistema ou cliente irritado. Ofereça uma solução imediata ou escalonamento imediato para engenharia." if state["sentiment"] == "Angry" or state["urgency"] == "Critical" else ""
    tratamento_vip = "⭐ CLIENTE VIP: Ofereça a opção de agendar uma chamada de suporte dedicada de 15 minutos." if state["account_level"] == "VIP" else ""

    prompt = f"""
    You are Natanzinho_Support, a customer support specialist for Neytans.
    Your task is to generate the next response that should be sent to the customer.

    {alerta_prioridade}
    {tratamento_vip}

    # Instructions
    - Always respond in Portuguese.
    - Be clear, objective, helpful and technical, yet highly polite.
    - Return only the message that should be sent to the customer.
    - Do not explain your reasoning, do not use markdown, and do not use headings.

    # Interactions History (Past Conversations)
    {texto_historico}

    # Context Data
    Sender email: {state["sender_email"]}
    Account Level: {state["account_level"]}
    Customer Sentiment: {state["sentiment"]}
    Urgency Level: {state["urgency"]}

    # New Customer Email (Answer this one now)
    "{state['body_email']}"

    Generate the customer reply now in email form using this information.
    """
    
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    response_ia = response.text

    return {
        "final_answer": response_ia,
        "history": [
            HumanMessage(content=state['body_email']),
            AIMessage(content=response_ia)
        ]
    }

# Node-4
def answer_commercial(state: GraphState) -> dict:
    print("\n🤝 [NÓ: RESPOSTA COMERCIAL]: Gerando proposta/retorno de negócios...")

    historico_mensagens = state.get("history") or []
    texto_historico = ""
    for msg in historico_mensagens:
        if isinstance(msg, HumanMessage):
            origem = "Cliente"
        else:
            origem = "Suporte"
        texto_historico += f"{origem}: {msg.content}\n"
    
    if not texto_historico:
        texto_historico = "Nenhuma interação anterior."
    
    tratamento_vip = "⭐ LEAD VIP: Trate como potencial parceiro estratégico nível Gold. Use tom altamente persuasivo." if state["account_level"] == "VIP" else ""

    prompt = f"""
    You are Natanzinho_Commercial, a customer support commercial specialist for Neytans.
    Your task is to generate the next response that should be sent to the customer.

    {tratamento_vip}

    # Instructions
    - Always respond in Portuguese.
    - Be professional, commercial, enthusiastic and concise.
    - Highlight our interest in evaluating solid opportunities.
    - Return only the message that should be sent to the customer.
    - Do not explain your reasoning, do not use markdown, and do not use headings.

    # Interactions History (Past Conversations)
    {texto_historico}

    # Context Data
    Sender email: {state["sender_email"]}
    Account Level: {state["account_level"]}
    Customer Sentiment: {state["sentiment"]}
    Urgency Level: {state["urgency"]}

    # New Customer Email (Answer this one now)
    "{state['body_email']}"

    Generate the customer reply now in email form using this information.
    """
    
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    response_ia = response.text

    return {
        "final_answer": response_ia,
        "history": [
            HumanMessage(content=state['body_email']),
            AIMessage(content=response_ia)
        ]
    }


# Send email - new node
def send_email_node(state: GraphState) -> dict:
    print("\n📧 [NÓ: ENVIO DE E-MAIL]: Preparando disparo via SMTP...")

    if not state.get("final_answer"):
        print("⚠️ [ENVIO]: Nenhuma resposta gerada no estado. Abortando envio automático.")
        return {}
    
    meu_email = os.getenv("EMAIL_ACCOUNT")
    minha_senha = os.getenv("EMAIL_PASSWORD")
    email_cliente = state["sender_email"]

    msg = MIMEMultipart()
    msg['From'] = meu_email
    msg['To'] = email_cliente
    msg['Subject'] = f"Re: Atendimento Neytans - Setor {state.get('destination_sector', 'Suporte')}"

    msg.attach(MIMEText(state["final_answer"], 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(meu_email, minha_senha)

        server.sendmail(meu_email, email_cliente, msg.as_string())
        server.quit()

        print(f"✅ [ENVIO CONCLUÍDO]: E-mail enviado com sucesso para {email_cliente}!")
    except Exception as e:
        print(f"❌ [ERRO NO ENVIO]: Falha ao disparar e-mail via SMTP: {e}")

    return {}

# Ler a caixa de entrada
def process_inbound_emails():
    print("\n📥 [SISTEMA]: Verificando novos e-mails não lidos no Gmail...")

    meu_email = os.getenv("EMAIL_ACCOUNT")
    minha_senha = os.getenv("EMAIL_PASSWORD")

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(meu_email, minha_senha)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()

        if not email_ids:
            print("📭 Caixa limpa! Nenhum e-mail novo encontrado.")
            return
        print(f"📩 {len(email_ids)} novo(s) e-mail(s) detectado(s). Processando o mais recente...")

        latest_email_id = email_ids[-1]
        status,data, = mail.fetch(latest_email_id, "(RFC822)")

        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                from_, encoding = decode_header(msg["From"])[0]

                if isinstance(from_, bytes):
                    from_ = from_.decode(encoding or "utf-8")

                if "<" in from_:
                    sender_email = from_.split("<")[1].replace(">", "").strip()
                else:
                    sender_email = from_.strip()

                sender_email = sender_email.strip().lower()

                body_email = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body_email = part.get_payload(decode=True).decode("utf-8")
                            break
                else:
                    body_email = msg.get_payload(decode=True).decode("utf-8")

                print(f"📨 Remetente: {sender_email}")
                print(f"📄 Conteúdo Lido:\n{body_email.strip()}")
                print("-" * 40)


                thread_clean = sender_email.replace("@", "_").replace(".", "_")
                config = {"configurable": {"thread_id": f"th_{thread_clean}"}}
                
                inputs = {
                    "sender_email": sender_email,
                    "body_email": body_email.strip(),
                    "destination_sector": None,
                    "urgency": None,
                    "sentiment": None,
                    "account_level": None,
                    "final_answer": None
                }

                print("🧠 [LANGGRAPH]: Iniciando processamento do Grafo...")
                app.invoke(inputs, config=config)

        mail.close()
        mail.logout()

    except Exception as e:
        print(f"❌ [ERRO IMAP]: Falha ao ler a caixa de entrada: {e}")
                


# ROUTE FUNCTION
def route_email(state: GraphState) -> str:
    sector = state["destination_sector"]

    if sector == "Finance":
        return "finance"
    
    elif sector == "Support":
        return "support"
    
    elif sector == "Commercial":
        return "commercial"
    
    else:
        print(f"⚠️ [ROTEADOR]: Setor detectado '{sector}' é inválido! Desviando para o Fallback.")
        return "fallback"


# Graph created

graph = StateGraph(GraphState)

graph.add_node("classify_email",
               classify_email)

graph.add_node("answer_finance",
               answer_finance)

graph.add_node("answer_support",
               answer_support)

graph.add_node("answer_commercial",
               answer_commercial)

graph.add_node("enrich_data",
               enrich_data)

graph.add_node("answer_fallback",
               answer_fallback)

graph.add_node("send_email_node",send_email_node)

# Edges

graph.set_entry_point("classify_email")

graph.add_edge("classify_email",
               "enrich_data")

graph.add_conditional_edges(
    "enrich_data",
    route_email,
    {
        "finance": "answer_finance",
        "support": "answer_support",
        "commercial": "answer_commercial",
        "fallback": "answer_fallback"
    }
                             )

graph.add_edge("answer_finance",
               "send_email_node")

graph.add_edge("answer_support",
               "send_email_node")

graph.add_edge("answer_commercial",
               "send_email_node")

graph.add_edge("answer_fallback",
               "send_email_node")

graph.add_edge("send_email_node",
               END)



# TEST
if __name__ == "__main__":
    print("🧪 [SISTEMA]: Inicializando banco de dados local da memória...")
    
    # O "with" garante que o arquivo de banco de dados feche corretamente se o código falhar
    with SqliteSaver.from_conn_string("memoria_grafo.db") as memory:
        
        # Compila o Grafo injetando o checkpointer de disco válido
        app = graph.compile(checkpointer=memory)
        
        # 🚀 Executa o leitor de e-mails reais ou mockados
        process_inbound_emails()

""" png_bytes = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
    with open("grafo_exemplo1.png", "wb") as f:
        f.write(png_bytes)
    print("\n🖼️ Imagem do grafo atualizada com sucesso em 'grafo_exemplo1.png'!")"""