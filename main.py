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
    
    urgency = state["urgency"]

    sentiment = state["sentiment"]

    account_level = state["account_level"]

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

# Node-2
def  answer_finance(state: GraphState) -> dict:

    prompt = f"""
You are Natanzinho_Finance, a customer support finance specialist for Neytans.

Your task is to generate the next response that should be sent to the customer.

# Instructions

- Always respond in the same language used by the customer.
- Be professional, friendly and concise.
- Follow all procedures and guidelines provided below.
- Return only the message that should be sent to the customer.
- Do not explain your reasoning.
- Do not use markdown.
- Do not use headings.



# Customer Info

Sender email: {state["sender_email"]}

# Email

{state['body_email']}

# Destination Sector

{state['destination_sector']}


Generate the customer reply now in email form using this informations.

 """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )


    return {"final_answer": response.text}



# Node-3
def answer_support(state: GraphState) -> dict:

    prompt= f"""
    You are Natanzinho_Support, a customer support specialist for Neytans.

Your task is to generate the next response that should be sent to the customer.

# Instructions

- Always respond in the Portuguese.
- Be professional, friendly and concise.
- Follow all procedures and guidelines provided below.
- Return only the message that should be sent to the customer.
- Do not explain your reasoning.
- Do not use markdown.
- Do not use headings.



# Customer Info

Sender email: {state["sender_email"]}

# Email

{state['body_email']}

# Destination Sector

{state['destination_sector']}


Generate the customer reply now in email form using this informations.

"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {"final_answer": response.text}

# Node-4
def answer_commercial(state:GraphState) -> dict:
    prompt = f"""
You are Natanzinho_Commercial, a customer support commercial specialist for Neytans.

Your task is to generate the next response that should be sent to the customer.

# Instructions

- Always respond in the Portuguese.
- Be professional, friendly and concise.
- Follow all procedures and guidelines provided below.
- Return only the message that should be sent to the customer.
- Do not explain your reasoning.
- Do not use markdown.
- Do not use headings.



# Customer Info

Sender email: {state["sender_email"]}

# Email

{state['body_email']}

# Destination Sector

{state['destination_sector']}


Generate the customer reply now in email form using this informations.


"""
    response = client.models.generate_content(
         model="gemini-2.5-flash",
         contents=prompt
    )

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

# Edges

graph.set_entry_point("classify_email")

graph.add_conditional_edges(
    "classify_email",
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

    "sender_email": "cliente@email.com",
    "body_email": "Gostaria de saber se vocês têm interesse em fechar uma parceria de vendas com a nossa distribuidora. Aguardo retorno do setor de vendas. ",
    "destination_sector": None,
    "final_answer": None
    
    }

    print("Iniciando teste Completo...")

    result = app.invoke(inputs)

    print("\n--- RESULTADO FINAL DO ESTADO ---")
    print("Setor Identificado:", result.get("destination_sector"))
    print("\nResposta Gerada:\n", result.get("final_answer"))

    png_bytes = app.get_graph().draw_mermaid_png(
                    draw_method=MermaidDrawMethod.API
    )

    with open("grafo_exemplo1.png", "wb") as f:
        f.write(png_bytes)