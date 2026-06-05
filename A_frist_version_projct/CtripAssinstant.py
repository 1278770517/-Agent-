import os
from datetime import datetime

from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient

from A_frist_version_projct.child_graph_basemodel import ToFlightBookingAssistant, ToBookCarRental, \
    ToHotelBookingAssistant, ToBookExcursion
from tools.car_tools import search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental
from tools.flights_tools import fetch_user_flight_information, search_flights, update_ticket_to_new_flight, \
    cancel_ticket
from tools.hotels_tools import search_hotels, book_hotel, update_hotel, cancel_hotel
from tools.retriever_vector import lookup_policy
from tools.trip_tools import search_trip_recommendations, book_excursion, update_excursion, cancel_excursion
from A_frist_version_projct.agbet_satte_Typeic import Projct_State
from langchain_community.tools import TavilySearchResults
class CtripAssinstant:
    def __init__(self,runnalbe:Runnable):
        """
                初始化助手的实例。
                :param runnable: 可以运行对象，通常是一个Runnable类型的
                """
        self.runnalbe=runnalbe
    def __call__(self, state:Projct_State,config: RunnableConfig):
        """
               调用节点，执行助手任务
               :param state: 当前工作流的状态
               :param Runnableconfig: 配置: 里面有旅客的信息
               :return:
               """

        while True:
            # config = config.get("configurable",{})
            # user_id = config.get("passenger_id")
            # state={**state, "user_info": user_id}
            # print(user_id)
            result=self.runnalbe.invoke(state)
            if result.tool_calls and(
                result.content or
                isinstance(result.content, list) and
                not result.content[0].get('text')
            ):
                message=state.get("messages")+[('user','请提供一个输出作为回应')]
                state={**state, "messages": message}
            else:
                break
        return {'messages': result}
 # search_tool=MultiServerMCPClient({'bing_search':bing_search})
os.environ["TAVILY_API_KEY"]='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'
tavily_tool = TavilySearchResults(max_results=1)

# part_1_tools = [
#                     tavily_tool,
#                     fetch_user_flight_information,
#                     search_flights,
#                     lookup_policy,
#                     update_ticket_to_new_flight,
#                     cancel_ticket,
#                     search_car_rentals,
#                     book_car_rental,
#                     update_car_rental,
#                     cancel_car_rental,
#                     search_hotels,
#                     book_hotel,
#                     update_hotel,
#                     cancel_hotel,
#                     search_trip_recommendations,
#                     book_excursion,
#                     update_excursion,
#                     cancel_excursion,
#                 ]
# safe_tools = [
#     tavily_tool,  # 搜索结果，例如航班信息
#     fetch_user_flight_information,       # 获取用户的航班信息
#     search_flights,                      # 搜索航班
#     lookup_policy,                       # 查看公司政策
#     search_car_rentals,                  # 搜索租车选项
#     search_hotels,                       # 搜索酒店
#     search_trip_recommendations,         # 搜索旅行推荐
# ]
#
# # 定义敏感工具列表，这些工具会更改用户的预订
# sensitive_tools = [
#     update_ticket_to_new_flight,         # 更新航班票务到新航班
#     cancel_ticket,                       # 取消票务
#     book_car_rental,                     # 预订租车
#     update_car_rental,                   # 更新租车预订
#     cancel_car_rental,                   # 取消租车预订
#     book_hotel,                          # 预订酒店
#     update_hotel,                        # 更新酒店预订
#     cancel_hotel,                        # 取消酒店预订
#     book_excursion,                      # 预订短途旅行
#     update_excursion,                    # 更新短途旅行预订
#     cancel_excursion,                    # 取消短途旅行预订
# ]
primary_assistant_tools = [
    tavily_tool,  # 假设TavilySearchResults是一个有效的搜索工具
    search_flights,  # 搜索航班的工具
    lookup_policy,  # 查找公司政策的工具
]
def run_CtripAssinstant()->CtripAssinstant:
    """
        创建一个助手节点
        :return: 返回一个助手节点对象
        """
    LLM = ChatTongyi(
        model='qwen-plus',  # 建议使用 qwen-plus 或 qwen-max，它们对工具调用支持更好
        api_key='sk-6b4cfd663e22498b8f82b39e798912c8',
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.8,
    )
    prompt=ChatPromptTemplate.from_messages([("system",
                "您是携程瑞士航空公司的客户服务助理。优先使用提供的工具搜索航班、公司政策和其他信息来帮助用户的查询。"
                "搜索时，请坚持不懈。如果第一次搜索没有结果，扩大您的查询范围。"
                "如果搜索为空，在放弃之前扩展您的搜索。\n\n当前用户:\n<User>\n{user_info}\n</User>"
                "\n当前时间: {time}.",),
                MessagesPlaceholder(variable_name='messages',optional=True),
                                             ]).partial(time=datetime.now())
    # bing_search={
    #     'url':'https://mcp.api-inference.modelscope.net/7c2a0f41978c41/sse',
    #     'transport':'sse'
    # }
    # search_tool=MultiServerMCPClient({'bing_search':bing_search})
    # os.environ["TAVILY_API_KEY"]='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'
    # tavily_tool = TavilySearchResults(max_results=1)

    runbale=prompt|LLM.bind_tools(primary_assistant_tools+[
        ToFlightBookingAssistant,  # 用于转交航班更新或取消的任务
        ToBookCarRental,  # 用于转交租车预订的任务
        ToHotelBookingAssistant,  # 用于转交酒店预订的任务
        ToBookExcursion,  # 用于转交旅行推荐和其他游览预订的任务
    ])
    return CtripAssinstant(runbale)
