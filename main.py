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
    pass

# Node-3
def answer_support(state: GraphState) -> dict:
    pass

# Node-4
def answer_commercial(state:GraphState) -> dict:
    pass

# TEST

if __name__ == "__main__":

    example_state = {

    "sender_email": "cliente@email.com",
    "body_email": "Olá, gostaria de saber o boleto da minha mensalidade que vence amanhã. Podem me enviar o código de barras?",
    "destination_sector": None,
    "final_answer": None
    
    }

    print("Iniciando teste do nó de classificação...")

    result = classify_email(example_state)

    print("Resultado do Nó 1:", result)
