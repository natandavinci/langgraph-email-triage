from typing import Optional
from typing_extensions import TypedDict

# State
class Email(TypedDict):

    sender_email: Optional[str]

    body_email: Optional[str]

    destination_sector: Optional[str]

    final_answer: Optional[str]

# Node-1
def classifie_email(state: Email):
    pass

# Node-2
def  answer_finance(state: Email):
    pass

# Node-3
def answer_support(state: Email):
    pass

# Node-4
def answer_commercial(state:Email):
    pass