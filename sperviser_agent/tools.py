from typing import Annotated

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.graph import MessagesState
from langgraph.prebuilt import InjectedState
from langgraph.types import interrupt, Command

from zhipuai import ZhipuAI
from util import ZHIPU_API
zhipu=ZhipuAI(api_key=ZHIPU_API)
@tool()
def web_search(query:Annotated[str,'输入需要查询的问题']):
    '这是一个查询工具可以进行网页搜索'
    interupted_inpute=interrupt(f"AI大模型尝试调用工具 `search_tool`来完成数据搜索，\n"
            "请审核并选择：批准（y）或直接给我工具执行的答案。"
        )
    if interupted_inpute['answer']=='y':
        result=zhipu.web_search( search_engine="search_std",
            search_query=query)
        if result:
            return result
        else:
            return '没有搜索到'
    else:
        return '输入其他终止搜索'
def rout_childgraph(*, agent_name: str, description: str | None = None):
    @tool(agent_name,description=description)
    def handoff_tool(state: Annotated[MessagesState, InjectedState],tool_call_id: Annotated[str, InjectedToolCallId])->Command:
        """
             执行实际的转接操作。

             创建一个工具消息表明转接成功，并返回一个命令对象指示流程控制器
             将控制权转移给指定代理，同时更新会话状态。

             参数:
                 state (MessagesState): 当前会话状态，包含消息历史等信息
                 tool_call_id (str): 工具调用的唯一标识符

             返回:
                 Command: 包含转接指令和状态更新的命令对象
             """
        # 构造工具消息，记录转接操作的成功执行

        toolmessage={
            'role':'tool',
            'content':'<UNK>',
            'tool_call_id':tool_call_id,
            'agent_name':agent_name,
        }
        return Command(
            goto=agent_name,
            update={**state,'message':state['message']+[toolmessage]},
            graph=Command.PARENT
        )

    return handoff_tool

assign_to_research_agent = rout_childgraph(
    agent_name="web_search",
    description="将任务分配给：research_agent智能体。",
)

assign_to_flight_booking_agent = rout_childgraph(
    agent_name="flight_booking_agent",
    description="将任务分配给：flight_booking_agent智能体。",
)
assign_to_hotel_booking_agent =rout_childgraph(
    agent_name="hotel_booking_agent",
    description="将任务分配给：hotel_booking_agent智能体。",
)
assign_to_car_rental_booking_agent = rout_childgraph(
    agent_name="car_rental_booking_agent",
    description="将任务分配给：car_rental_booking_agent智能体。",
)
assign_to_excursion_booking_agent = rout_childgraph(
    agent_name="excursion_booking_agent",
    description="将任务分配给：excursion_booking_agent智能体。",
)