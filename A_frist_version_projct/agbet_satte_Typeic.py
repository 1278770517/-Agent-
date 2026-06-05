from typing import TypedDict, Annotated,Literal,Optional

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


def update_dialog(left:list,right:Optional[str])->list:
    if right==None:
        return left
    if right=='pop':
        return left[:-1]
    else:
        return left+[right]
class Projct_State(TypedDict):
    messages: Annotated[list[AnyMessage],add_messages]
    user_info:str
    dialog_state: Annotated[list[Literal[
        "ctripassitant",
        "update_flight",
        "book_car_rental",
        "book_hotel",
        "book_excursion",
    ]],update_dialog]