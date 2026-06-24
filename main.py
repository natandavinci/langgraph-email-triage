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
from langgraph.checkpoint.memory import MemorySaver

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

    history: Optional[str]

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
def answer_fallback(state:GraphState) -> dict:
    print("\n🚨 [NÓ: FALLBACK]: Setor inválido ou falha de triagem. Gerando resposta de segurança...")
    
    prompt = f"""
    You are Natanzinho_Specialist, a senior customer relations coordinator at Neytans.
    We had a minor internal routing delay with your ticket, so I am taking over personally.
    
    Write a very polite email to the customer stating that their request has been received 
    and a specialized human manager is reviewing it right now to give a precise answer within the next few hours.
    
    # Instructions
    - Respond in Portuguese.
    - Be extremely polite, professional, and reassuring.
    - Do not use markdown or headings.
    
    # Customer Email
    "{state['body_email']}"
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {"final_answer": response.text, "destination_sector": "Human_Contigency"}




# Node-2
def  answer_finance(state: GraphState) -> dict:

    print("\n💰 [NÓ: RESPOSTA FINANCEIRO]: Gerando resposta estratégica...")
    historico_atual = state.get("history") or []
    texto_historico = "\n".join(historico_atual) if historico_atual else "Nenhuma interação anterior."
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

    historico_atual.append(f"Cliente: {state['body_email']}")
    historico_atual.append(f"Suporte: {response_ia}")
    
    return {"final_answer": response_ia,
            "history": historico_atual}



# Node-3
def answer_support(state: GraphState) -> dict:

    print("\n🛠️ [NÓ: RESPOSTA SUPORTE]: Gerando resposta técnica...")

    historico_atual = state.get("history") or []
    texto_historico = "\n".join(historico_atual) if historico_atual else "Nenhuma interação anterior."
    
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

    historico_atual.append(f"Cliente: {state['body_email']}")
    historico_atual.append(f"Suporte: {response_ia}")
    
    return {"final_answer": response_ia,
            "history": historico_atual}

# Node-4
def answer_commercial(state:GraphState) -> dict:
    print("\n🤝 [NÓ: RESPOSTA COMERCIAL]: Gerando proposta/retorno de negócios...")

    historico_atual = state.get("history") or []
    texto_historico = "\n".join(historico_atual) if historico_atual else "Nenhuma interação anterior."
    
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

    historico_atual.append(f"Cliente: {state['body_email']}")
    historico_atual.append(f"Suporte: {response_ia}")
    
    return {"final_answer": response_ia,
            "history": historico_atual}

def route_email(state: GraphState) -> str:
    sector = state["destination_sector"]

    if sector == "Finance":
        return "answer_finance"
    
    elif sector == "Support":
        return "answer_support"
    
    elif sector == "Commercial":
        return "answer_commercial"
    
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
        "answer_commercial": "answer_commercial",
        "fallback": "answer_fallback"
    }
                             )

graph.add_edge("answer_finance",
               END)

graph.add_edge("answer_support",
               END)

graph.add_edge("answer_commercial",
               END)

graph.add_edge("answer_fallback",
               END)

memory = MemorySaver()

app = graph.compile(checkpointer=memory)


# TEST

if __name__ == "__main__":
   # Criamos a configuração da Thread
    config = {"configurable": {"thread_id": "teste_resiliencia_999"}}

    # --- CENÁRIO DE INCÊNDIO: Forçando uma falha de Roteamento ---
    # Imagine que por algum motivo o estado foi corrompido ou a IA viajou e carimbou "Recursos_Humanos"
    email_com_erro = {
        "sender_email": "usuario@email.com",
        # Um texto completamente aleatório e confuso que não pertence a nenhum setor
        "body_email": "xyz123999 dasdaaslkjdas dsa;ldkas;l dsa d;sa lkd;sa kdas;lkd;sa kda",
        "destination_sector": None, 
        "urgency": None,
        "sentiment": None,
        "account_level": None,
        "history": [],
        "final_answer": None
    }

    print("🔥 DISPARANDO TESTE DE ESTRESSE (SETOR INVÁLIDO)...")
    
    # O grafo deve rodar, passar pelo enrich_data, cair na aresta, perceber o erro e desviar para o Fallback
    resultado_seguro = app.invoke(email_com_erro, config=config)

    print("\n--- 🏁 RELATÓRIO DE CONTINGÊNCIA ---")
    print(f"📍 Setor Ajustado no Fallback: {resultado_seguro.get('destination_sector')}")
    print(f"🎭 Sentimento Original:        {resultado_seguro.get('sentiment')}")
    
    print("\n📧 Resposta de Emergência Gerada:\n")
    print("-" * 60)
    print(resultado_seguro.get("final_answer"))
    print("-" * 60)





    png_bytes = app.get_graph().draw_mermaid_png(
                    draw_method=MermaidDrawMethod.API
    )

    with open("grafo_exemplo1.png", "wb") as f:
        f.write(png_bytes)




