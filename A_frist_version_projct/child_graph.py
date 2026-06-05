from fastapi.dependencies.utils import add_non_field_param_to_dependency
from langchain_core.messages import ToolMessage
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from A_frist_version_projct.agbet_satte_Typeic import Projct_State
from A_frist_version_projct.child_graph_basemodel import CompleteOrEscalate
from A_frist_version_projct.child_graph_runnnable import book_flight_runnable, update_flight_safe_tools, \
    update_flight_sensitive_tools, book_car_rental_runnable, book_car_rental_safe_tools, \
    book_car_rental_sensitive_tools, book_hotel_runnable, book_hotel_safe_tools, book_hotel_sensitive_tools, \
    book_excursion_runnable, book_excursion_safe_tools, book_excursion_sensitive_tools
from A_frist_version_projct.enter_node import enternode
from A_frist_version_projct.CtripAssinstant import CtripAssinstant
from tools.tools_handler import create_tool_node_with_fallback


def book_fligt_childgrapg(graph:StateGraph) -> StateGraph:
    sensative_tool={i.name for i in update_flight_sensitive_tools}
    safe_tool={i.name for i in update_flight_safe_tools}
    graph.add_node('book_fligt_enternode',enternode('book_fligt_enternode','update_flight'))
    graph.add_node('update_flight',CtripAssinstant(book_flight_runnable))
    graph.add_node('update_flight_sennsative',create_tool_node_with_fallback(update_flight_sensitive_tools))
    graph.add_node('update_flight_safe', create_tool_node_with_fallback(update_flight_safe_tools))
    graph.add_edge('book_fligt_enternode','update_flight')
    def root_condition(state: dict):
        print('+++++++++++root_condition+++++++++++')
        if tools_condition(state)==END:
            print('use_end')
            return END
        if tools_condition(state)=='tools':
            tool_list = state['messages'][-1].tool_calls
            if any(tc['name']==CompleteOrEscalate.__name__ for tc in tool_list):
                return 'leave_node'
            if all(tc['name']in safe_tool for tc in tool_list):
                return 'update_flight_safe'
            return 'update_flight_sennsative'
    def leave_node(state: dict):
        print('+++++++++++leave_node+++++++++++')
        messages=[]
        if state['messages'][-1].tool_calls:
            messages = [ToolMessage(content='用户已退出航班/租车/酒店/游览助手，请恢复主助理身份直接为用户服务',tool_call_id=state['messages'][-1].tool_calls[0]['id'])]
        return {
            'messages': messages,
            'dialog_state':'pop'
        }

    graph.add_node('leave_node',leave_node)

    graph.add_conditional_edges('update_flight',root_condition,{
        END:END,
        'update_flight_sennsative':'update_flight_sennsative',
        'update_flight_safe':'update_flight_safe',
        'leave_node':'leave_node'
    })
    graph.add_edge('update_flight_safe','update_flight')
    graph.add_edge('update_flight_sennsative', 'update_flight')

    return graph

def build_car_graph(builder: StateGraph) -> StateGraph:
    # 租车助理 的子工作流
    # 添加入口节点，当需要预订租车时使用
    builder.add_node(
        "enter_book_car_rental",
        enternode("Car Rental Assistant", "book_car_rental"),  # 创建入口节点，指定助理名称和新对话状态
    )
    builder.add_node("book_car_rental",CtripAssinstant (book_car_rental_runnable))  # 添加处理租车预订的实际节点
    builder.add_edge("enter_book_car_rental", "book_car_rental")  # 连接入口节点到实际处理节点

    # 添加安全工具和敏感工具的节点
    builder.add_node(
        "book_car_rental_safe_tools",
        create_tool_node_with_fallback(book_car_rental_safe_tools),  # 安全工具节点，通常只读查询
    )
    builder.add_node(
        "book_car_rental_sensitive_tools",
        create_tool_node_with_fallback(book_car_rental_sensitive_tools),  # 敏感工具节点，包含可能修改数据的操作
    )

    def route_book_car_rental(state: dict):
        """
        根据当前状态路由租车预订流程。

        :param state: 当前对话状态字典
        :return: 下一步应跳转到的节点名
        """
        route = tools_condition(state)  # 判断下一步的方向
        if route == END:
            return END  # 如果结束条件满足，则返回END
        tool_calls = state["messages"][-1].tool_calls  # 获取最后一条消息中的工具调用
        did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)  # 检查是否调用了CompleteOrEscalate
        if did_cancel:
            return "leave_node"  # 如果用户请求取消或退出，则跳转至leave_skill节点
        safe_toolnames = [t.name for t in book_car_rental_safe_tools]  # 获取所有安全工具的名字
        if all(tc["name"] in safe_toolnames for tc in tool_calls):  # 如果所有调用的工具都是安全工具
            return "book_car_rental_safe_tools"  # 跳转至安全工具处理节点
        return "book_car_rental_sensitive_tools"  # 否则跳转至敏感工具处理节点

    # 添加边，连接敏感工具和安全工具节点回到租车预订处理节点
    builder.add_edge("book_car_rental_sensitive_tools", "book_car_rental")
    builder.add_edge("book_car_rental_safe_tools", "book_car_rental")

    # 根据条件路由租车预订流程
    builder.add_conditional_edges(
        "book_car_rental",
        route_book_car_rental,
        [
            "book_car_rental_safe_tools",
            "book_car_rental_sensitive_tools",
            'leave_node',
            END,
        ],
    )
    return builder
def builder_hotel_graph(builder: StateGraph) -> StateGraph:
    # 添加入口节点，当需要预订酒店时使用
    builder.add_node(
        "enter_book_hotel",
        enternode("酒店预订助理", "book_hotel"),  # 创建入口节点，指定助理名称和新对话状态
    )
    builder.add_node("book_hotel", CtripAssinstant(book_hotel_runnable))  # 添加处理酒店预订的实际节点
    builder.add_edge("enter_book_hotel", "book_hotel")  # 连接入口节点到实际处理节点

    # 添加安全工具和敏感工具的节点
    builder.add_node(
        "book_hotel_safe_tools",
        create_tool_node_with_fallback(book_hotel_safe_tools),  # 安全工具节点，通常只读查询
    )
    builder.add_node(
        "book_hotel_sensitive_tools",
        create_tool_node_with_fallback(book_hotel_sensitive_tools),  # 敏感工具节点，包含可能修改数据的操作
    )

    def route_book_hotel(state: dict):
        """
        根据当前状态路由酒店预订流程。

        :param state: 当前对话状态字典
        :return: 下一步应跳转到的节点名
        """
        route = tools_condition(state)  # 判断下一步的方向
        if route == END:
            return END  # 如果结束条件满足，则返回END
        tool_calls = state["messages"][-1].tool_calls  # 获取最后一条消息中的工具调用
        did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)  # 检查是否调用了CompleteOrEscalate
        if did_cancel:
            return "leave_node"  # 如果用户请求取消或退出，则跳转至leave_skill节点
        safe_toolnames = [t.name for t in book_hotel_safe_tools]  # 获取所有安全工具的名字
        if all(tc["name"] in safe_toolnames for tc in tool_calls):  # 如果所有调用的工具都是安全工具
            return "book_hotel_safe_tools"  # 跳转至安全工具处理节点
        return "book_hotel_sensitive_tools"  # 否则跳转至敏感工具处理节点

    # 添加边，连接敏感工具和安全工具节点回到酒店预订处理节点
    builder.add_edge("book_hotel_sensitive_tools", "book_hotel")
    builder.add_edge("book_hotel_safe_tools", "book_hotel")

    # 根据条件路由酒店预订流程
    builder.add_conditional_edges(
        "book_hotel",
        route_book_hotel,
        ["leave_node", "book_hotel_safe_tools", "book_hotel_sensitive_tools", END],
    )
    return builder
def builder_excursion_graph(builder: StateGraph) -> StateGraph:
    # 添加入口节点，当需要预订游览或获取旅行推荐时使用
    builder.add_node(
        "enter_book_excursion",
        enternode("旅行推荐助理", "book_excursion"),  # 创建入口节点，指定助理名称和新对话状态
    )
    builder.add_node("book_excursion", CtripAssinstant(book_excursion_runnable))  # 添加处理游览预订的实际节点
    builder.add_edge("enter_book_excursion", "book_excursion")  # 连接入口节点到实际处理节点

    # 添加安全工具和敏感工具的节点
    builder.add_node(
        "book_excursion_safe_tools",
        create_tool_node_with_fallback(book_excursion_safe_tools),  # 安全工具节点，通常只读查询
    )
    builder.add_node(
        "book_excursion_sensitive_tools",
        create_tool_node_with_fallback(book_excursion_sensitive_tools),  # 敏感工具节点，包含可能修改数据的操作
    )

    def route_book_excursion(state: dict):
        """
        根据当前状态路由游览预订流程。

        :param state: 当前对话状态字典
        :return: 下一步应跳转到的节点名
        """
        route = tools_condition(state)  # 判断下一步的方向
        if route == END:
            return END  # 如果结束条件满足，则返回END
        tool_calls = state["messages"][-1].tool_calls  # 获取最后一条消息中的工具调用
        did_cancel = any(tc["name"] == CompleteOrEscalate.__name__ for tc in tool_calls)  # 检查是否调用了CompleteOrEscalate
        if did_cancel:
            return "leave_node"  # 如果用户请求取消或退出，则跳转至leave_skill节点
        safe_toolnames = [t.name for t in book_excursion_safe_tools]  # 获取所有安全工具的名字
        if all(tc["name"] in safe_toolnames for tc in tool_calls):  # 如果所有调用的工具都是安全工具
            return "book_excursion_safe_tools"  # 跳转至安全工具处理节点
        return "book_excursion_sensitive_tools"  # 否则跳转至敏感工具处理节点

    # 添加边，连接敏感工具和安全工具节点回到游览预订处理节点
    builder.add_edge("book_excursion_sensitive_tools", "book_excursion")
    builder.add_edge("book_excursion_safe_tools", "book_excursion")

    # 根据条件路由游览预订流程
    builder.add_conditional_edges(
        "book_excursion",
        route_book_excursion,
        ["book_excursion_safe_tools", "book_excursion_sensitive_tools", "leave_node", END],
    )
    return builder