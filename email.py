from typing import Optional
from typing_extensions import TypedDict

# State
class GraphState(TypedDict):

    sender_email: Optional[str]

    body_email: Optional[str]

    destination_sector: Optional[str]

    final_answer: Optional[str]

# Node-1
def classify_email(state: GraphState) -> dict:
    pass

# Node-2
def  answer_finance(state: GraphState) -> dict:
    pass

# Node-3
def answer_support(state: GraphState) -> dict:
    pass

# Node-4
def answer_commercial(state:GraphState) -> dict:
    pass