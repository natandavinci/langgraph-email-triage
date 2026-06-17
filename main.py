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

class EmailClassification(BaseModel):
    sector: Literal["Finance", "Support", "Commercial"] = Field(
        description=" The destination sector base on the email content "
    )

# Node-1
def classify_email(state: GraphState) -> dict:

    body_email = state["body_email"]

    prompt = f"Classifique o seguinte e-mail em um dos setores válidos: {body_email}"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(

            response_mime_type="application/json",
            response_schema=EmailClassification,
        )
    )
    
    extract_data = json.loads(response.text)

    return {"destination_sector": extract_data["sector"]}

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
    pass

# TEST

if __name__ == "__main__":

    example_state = {

    "sender_email": "cliente@email.com",
    "body_email": "Preciso de um suporte com meu sistema, pode me direcionar? o sistema não mostra os produtos",
    "destination_sector": "Support",
    "final_answer": None
    
    }

    print("Iniciando teste do node 3...")

    result = answer_support(example_state)

    print("Resultado do Nó 3:", result)
    print("\nTexto da Resposta Gerada:\n", result["final_answer"])
