from typing import (
    Optional,
    Literal)
from typing_extensions import TypedDict
from google import genai
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

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

class destination_sector(BaseModel):
    sector: Literal["Finance", "Support", "Commercial"] = Field(
        description=" The destination sector base on the email content "
    )

# Node-1
def classify_email(state: GraphState) -> dict:

    body_email = state["body_email"]

    prompt = f"Classifique o seguinte e-mail em um dos setores válidos: {body_email}"
    
    response = client.models.generate_content(
        model="gemini-2.5-flah",
        contents=prompt
    )
    

    return {"destination_sector": response.destination_sector}

# Node-2
def  answer_finance(state: GraphState) -> dict:
    pass

# Node-3
def answer_support(state: GraphState) -> dict:
    pass

# Node-4
def answer_commercial(state:GraphState) -> dict:
    pass