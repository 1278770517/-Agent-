from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from sperviser_agent.llm import llm
from sperviser_agent.tools import web_search, assign_to_research_agent, assign_to_flight_booking_agent, \
    assign_to_hotel_booking_agent, assign_to_car_rental_booking_agent, assign_to_excursion_booking_agent
from tools.car_tools import search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental
from tools.flights_tools import search_flights, update_ticket_to_new_flight, cancel_ticket
from tools.hotels_tools import search_hotels, book_hotel, update_hotel, cancel_hotel
from tools.retriever_vector import lookup_policy
from tools.trip_tools import search_trip_recommendations, book_excursion, update_excursion, cancel_excursion

memory = InMemorySaver()
web_search=create_agent(
    model=llm,
    tool=[web_search],
    system_prompt="你是一个网络搜索的智能体(Agent)。\n\n"
        "指令：\n"
        "- 仅网络数据获取、网络查询、数据查询相关的任务\n"
        "- 回复时仅包含工作结果，不要包含任何其他文字",
    checkpointer=memory,
    name="web_search"
)

update_flight_safe_tools = [search_flights, lookup_policy]
update_flight_sensitive_tools = [update_ticket_to_new_flight, cancel_ticket]

# 合并所有工具
update_flight_tools = update_flight_safe_tools + update_flight_sensitive_tools
# 航班预订的 子智能体
flight_booking_agent = create_react_agent(
    model=llm,
    tools=update_flight_tools,
    prompt=(
        "您是专门处理航班查询，改签政策查询，改签和预定的智能体(Agent)。\n\n"
        "指令：\n"
        "- 在搜索航班时，请坚持不懈。如果第一次搜索没有结果，请扩大查询范围。\n"
        "- 如果您的工具都不适用或客户改变主意，直接回复，并给出理由。\n"
        "- 回复时仅包含工作结果，不要包含任何其他文字"
    ),
    checkpointer=memory,
    name="flight_booking_agent",
)

book_hotel_safe_tools = [search_hotels]
book_hotel_sensitive_tools = [book_hotel, update_hotel, cancel_hotel]

# 合并所有工具
book_hotel_tools = book_hotel_safe_tools + book_hotel_sensitive_tools

# 酒店处理的 子智能体
hotel_booking_agent = create_react_agent(
    model=llm,
    tools=book_hotel_tools,
    prompt=(
        "您是专门处理酒店查询，酒店预定，酒店订单修改的智能体(Agent)。\n\n"
        "指令：\n"
        "- 在搜索时，请坚持不懈。如果第一次搜索没有结果，请扩大查询范围。\n"
        "- 根据用户的偏好搜索可用酒店，并与客户确认预订详情。\n"
        "- 如果您的工具都不适用或客户改变主意，直接回复，并给出理由。\n"
        "- 回复时仅包含工作结果，不要包含任何其他文字"
    ),
    checkpointer=memory,
    name="hotel_booking_agent",
)

# 定义安全工具（只读操作）和敏感工具（涉及更改的操作）
book_car_rental_safe_tools = [search_car_rentals]
book_car_rental_sensitive_tools = [
    book_car_rental,
    update_car_rental,
    cancel_car_rental,
]

# 合并所有工具
book_car_rental_tools = book_car_rental_safe_tools + book_car_rental_sensitive_tools
# 汽车租赁处理的 子智能体
car_rental_booking_agent = create_react_agent(
    model=llm,
    tools=book_car_rental_tools,
    prompt=(
        "您是专门处理汽车租赁查询，汽车租赁预定，汽车租赁订单修改的智能体(Agent)。\n\n"
        "指令：\n"
        "- 在搜索时，请坚持不懈。如果第一次搜索没有结果，请扩大查询范围。\n"
        "- 根据用户的偏好搜索可用租车，并与客户确认预订详情。\n"
        "- 如果您的工具都不适用或客户改变主意，直接回复，并给出理由。\n"
        "- 回复时仅包含工作结果，不要包含任何其他文字"
    ),
    name="car_rental_booking_agent",
)

# 定义安全工具（只读操作）和敏感工具（涉及更改的操作）
book_excursion_safe_tools = [search_trip_recommendations]
book_excursion_sensitive_tools = [book_excursion, update_excursion, cancel_excursion]

# 合并所有工具
book_excursion_tools = book_excursion_safe_tools + book_excursion_sensitive_tools
# 旅行推荐处理的 子智能体
excursion_booking_agent = create_react_agent(
    model=llm,
    tools=book_excursion_tools,
    prompt=(
        "您是专门处理旅行推荐查询，旅行产品预定，旅行订单修改的智能体(Agent)。\n\n"
        "指令：\n"
        "- 在搜索时，请坚持不懈。如果第一次搜索没有结果，请扩大查询范围。\n"
        "- 根据用户的偏好搜索可行的旅行推荐，并与客户确认预订详情。\n"
        "- 如果您的工具都不适用或客户改变主意，直接回复，并给出理由。\n"
        "- 回复时仅包含工作结果，不要包含任何其他文字"
    ),
    name="excursion_booking_agent",
)
supervisor_agent = create_react_agent(
    model=llm,
    tools=[assign_to_research_agent, assign_to_flight_booking_agent, assign_to_hotel_booking_agent, assign_to_car_rental_booking_agent, assign_to_excursion_booking_agent],
    prompt=(
        "你是一个监督者或者管理者，管理五个智能体：\n"
        "- 网络搜索智能体：分配与网络搜索、数据查询相关的任务\n"
        "- 航班预订能体：分配与航班查询，预定，改签等相关的任务\n"
        "- 酒店预订智能体：分配与酒店查询，预定，修改订单等相关的任务\n"
        "- 汽车租赁预定智能体：分配与汽车租赁查询，预定，修改订单等相关的任务\n"
        "- 旅行产品预定智能体：分配与旅行推荐查询，预定，修改订单等相关的任务\n"
        "处理规则：\n"
        "1. 如果问题属于以下类别，直接回答：\n"
        "   - 可以根据上下文记录直接回答的内容（如'你的航班信息，起飞时间等'）。\n"
        "   - 不需要工具的一般咨询（如'你好'）。\n"
        "   - 确认类问题（如'你收到我的请求了吗'）。\n"
        "2. 其他情况按类型分配给对应智能体。\n"
        "3. 一次只分配一个任务给一个智能体。\n"
        "4. 不要自己执行需要工具的任务。\n"
    ),
    # checkpointer=memory,
    name="supervisor",
)