from typing import Callable

from langchain_core.messages import ToolMessage

from A_frist_version_projct.agbet_satte_Typeic import Projct_State

def enternode(assistant_name:str,diaoge_state:str)->Callable:

    def create_enternode(state:dict):

        messages_state=state['messages'][-1]
        toocall=messages_state.tool_calls[0]['id']
        return {'messages':[ToolMessage(
            content=f"现在助手是{assistant_name}。请回顾上述主助理与用户之间的对话。"
                            f"用户的意图尚未满足。使用提供的工具协助用户。记住，您是{assistant_name}，"
                            "并且预订、更新或其他操作未完成，直到成功调用了适当的工具。"
                            "如果用户改变主意或需要帮助进行其他任务，请调用CompleteOrEscalate函数让主要的主助理接管。"
                            "不要提及你是谁——仅作为助理的代理。",
            tool_call_id=toocall
        )],
        'dialog_state':diaoge_state,}

    return create_enternode