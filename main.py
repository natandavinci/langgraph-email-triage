from typing import (
    Optional,
    Literal)
from typing_extensions import TypedDict
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import json
from langgraph.graph import StateGraph, END
from langchain_core.runnables.graph import MermaidDrawMethod

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
# Node-2
def  answer_finance(state: GraphState) -> dict:

    print("\n💰 [NÓ: RESPOSTA FINANCEIRO]: Gerando resposta estratégica...")
    
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

    # Context Data
    Sender email: {state["sender_email"]}
    Account Level: {state["account_level"]}
    Customer Sentiment: {state["sentiment"]}
    Urgency Level: {state["urgency"]}

    # Customer Email
    {state['body_email']}

    Generate the customer reply now in email form using this information.
    """
    
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return {"final_answer": response.text}



# Node-3
def answer_support(state: GraphState) -> dict:

    print("\n🛠️ [NÓ: RESPOSTA SUPORTE]: Gerando resposta técnica...")
    
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

    # Context Data
    Sender email: {state["sender_email"]}
    Account Level: {state["account_level"]}
    Customer Sentiment: {state["sentiment"]}
    Urgency Level: {state["urgency"]}

    # Customer Email
    {state['body_email']}

    Generate the customer reply now in email form using this information.
    """
    
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return {"final_answer": response.text}

# Node-4
def answer_commercial(state:GraphState) -> dict:
    print("\n🤝 [NÓ: RESPOSTA COMERCIAL]: Gerando proposta/retorno de negócios...")
    
    # Tratamento focado em conversão e retenção de parceiros de alto valor
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

    # Context Data
    Sender email: {state["sender_email"]}
    Account Level: {state["account_level"]}

    # Customer Email
    {state['body_email']}

    Generate the customer reply now in email form using this information.
    """
    
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return {"final_answer": response.text}

def route_email(state: GraphState) -> str:
    sector = state["destination_sector"]

    if sector == "Finance":
        return "answer_finance"
    
    elif sector == "Support":
        return "answer_support"
    
    elif sector == "Commercial":
        return "answer_commercial"


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

# Edges

graph.set_entry_point("classify_email")

graph.add_edge("classify_email",
               "enrich_data")

graph.add_conditional_edges(
    "enrich_data",
    route_email,
    {
        "answer_finance": "answer_finance",
        "answer_support": "answer_support",
        "answer_commercial": "answer_commercial"
    }
                             )

graph.add_edge("answer_finance",
               END)

graph.add_edge("answer_support",
               END)

graph.add_edge("answer_commercial",
               END)

app = graph.compile()


# TEST

if __name__ == "__main__":
    inputs = {
        # Testando com um e-mail que está na nossa lista VIP interna do nó enrich_data
        "sender_email": "rodrigo_premium@email.com",
        "body_email": "Estou há duas horas tentando acessar o painel financeiro e a página só dá erro 500! Quero meu estorno agora ou vou acionar o meu jurídico. Isso é inadmissível para o valor que eu pago!",
        "destination_sector": None,
        "urgency": None,
        "sentiment": None,
        "account_level": None,
        "final_answer": None
    }

    print("🔥 Iniciando teste do Triador Inteligente Enterprise...")

    result = app.invoke(inputs)

    print("\n--- 🏁 RELATÓRIO FINAL DO GRAFO ---")
    print(f"📍 Setor Destino:   {result.get('destination_sector')}")
    print(f"🔥 Nível de Urgência: {result.get('urgency')}")
    print(f"🎭 Sentimento:       {result.get('sentiment')}")
    print(f"💎 Nível de Conta:   {result.get('account_level')}")
    
    print("\n📧 Resposta Gerada Para Envio:\n")
    print("-" * 60)
    print(result.get("final_answer"))
    print("-" * 60)

    # Atualiza a imagem do Grafo
    png_bytes = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
    with open("grafo_exemplo1.png", "wb") as f:
        f.write(png_bytes)
    print("\n🖼️ Imagem do grafo atualizada com sucesso em 'grafo_exemplo1.png'!")