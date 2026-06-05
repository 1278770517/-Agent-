# 这是我调试大模型的万能联网层的patch，包含同步/异步 流式/非流式，可以查看给大模型的输入/输出，纯数据层面的逻辑解耦。中间变量，你还是在相关函数中打印日志或者设置断点。
# if True:
#     # --- 拦截原始 HTTP 请求/响应（支持普通 JSON + SSE 流）---
#     import httpx
#     import json
#
#
#     def _extract_and_print_json_from_text(text: str, label: str):
#         """
#         尝试从文本中提取 JSON：
#         - 如果是纯 JSON，直接解析；
#         - 如果是 SSE 格式（含 'data: {...}'），提取所有 data 行并解析。
#         """
#         text = text.strip()
#         if not text:
#             print(f"【{label}】空内容")
#             return
#
#         # 判断是否为 SSE 格式（简单启发式：包含 event: 和 data:）
#         if 'event:' in text and 'data:' in text:
#             lines = text.splitlines()
#             json_blobs = []
#             for line in lines:
#                 if line.startswith('data:'):
#                     json_str = line[5:].strip()  # 去掉 "data:"
#                     if json_str:
#                         json_blobs.append(json_str)
#
#             if json_blobs:
#                 print(f"【{label} (SSE)】")
#                 for blob in json_blobs:
#                     try:
#                         parsed = json.loads(blob)
#                         print(json.dumps(parsed, ensure_ascii=False, indent=2))
#                     except Exception as e:
#                         print(f"【{label} - SSE data 解析失败】", str(e), repr(blob[:150]))
#             else:
#                 print(f"【{label}】SSE 格式但无有效 data")
#         else:
#             # 尝试作为普通 JSON 解析
#             try:
#                 parsed = json.loads(text)
#                 print(f"【{label}】")
#                 print(json.dumps(parsed, ensure_ascii=False, indent=2))
#             except Exception as e:
#                 print(f"【{label}（非JSON）】", str(e), repr(text[:200]))
#
#
#     # ========== 同步 send 补丁 ==========
#     _original_send = httpx.Client.send
#
#
#     def _patched_send(self, request: httpx.Request, **kwargs):
#         # 打印请求
#         if request.content:
#             try:
#                 req_json = json.loads(request.content)
#                 print("【LLM 原始请求 (Sync)】")
#                 print(json.dumps(req_json, ensure_ascii=False, indent=2))
#             except Exception as e:
#                 print("【LLM 原始请求（非JSON）】", str(e), repr(request.content[:300]))
#         else:
#             print("【LLM 原始请求 (Sync)】无请求体")
#
#         # 发送请求
#         response = _original_send(self, request, **kwargs)
#
#         # 读取并解析响应
#         try:
#             response.read()
#             raw_text = response.content.decode('utf-8', errors='replace')
#             _extract_and_print_json_from_text(raw_text, "LLM 原始响应 (Sync)")
#         except Exception as e:
#             print("【LLM 同步响应读取失败】", str(e))
#
#         return response
#
#
#     # ========== 异步 send 补丁 ==========
#     _original_async_send = httpx.AsyncClient.send
#
#
#     async def _patched_async_send(self, request: httpx.Request, **kwargs):
#         # 打印请求
#         if request.content:
#             try:
#                 req_json = json.loads(request.content)
#                 print("【LLM 原始请求 (Async)】")
#                 print(json.dumps(req_json, ensure_ascii=False, indent=2))
#             except Exception as e:
#                 print("【LLM 原始请求（非JSON）】", str(e), repr(request.content[:300]))
#         else:
#             print("【LLM 原始请求 (Async)】无请求体")
#
#         # 发送请求
#         response = await _original_async_send(self, request, **kwargs)
#
#         # 读取并解析响应
#         try:
#             await response.aread()
#             raw_text = response.content.decode('utf-8', errors='replace')
#             _extract_and_print_json_from_text(raw_text, "LLM 原始响应 (Async)")
#         except Exception as e:
#             print("【LLM 异步响应读取失败】", str(e))
#
#         return response
#
#
#     # ========== 应用补丁 ==========
#     httpx.Client.send = _patched_send
#     httpx.AsyncClient.send = _patched_async_send
#
#     print("【日志】✅ 已拦截所有 LLM 的原始 HTTP 通信（支持 JSON / SSE 流）")
#
#     # ========== 在文件最顶部添加 ==========
#     import requests
#     import json
#
#
#     def _extract_and_print_json_from_text_for_requests(text: str, label: str):
#         """
#         尝试从文本中提取 JSON（与 httpx 版本逻辑一致）
#         """
#         text = text.strip()
#         if not text:
#             print(f"【{label}】空内容")
#             return
#
#         try:
#             parsed = json.loads(text)
#             print(f"【{label}】")
#             print(json.dumps(parsed, ensure_ascii=False, indent=2))
#         except Exception as e:
#             print(f"【{label}（非JSON）】", str(e), repr(text[:200]))
#
#
#     # ========== Patch requests ==========
#     _original_post = requests.Session.post
#     _original_get = requests.Session.get
#
#
#     def _patched_post(self, url, **kwargs):
#         # 判断是否是 DashScope 的请求
#         if "dashscope.aliyuncs.com" in url:
#             print("【DashScope 原始请求 (POST)】")
#             if 'json' in kwargs and kwargs['json']:
#                 print(json.dumps(kwargs['json'], ensure_ascii=False, indent=2))
#             elif 'data' in kwargs and kwargs['data']:
#                 _extract_and_print_json_from_text_for_requests(str(kwargs['data']), "DashScope 原始请求 (POST data)")
#             else:
#                 print("无请求体")
#
#         # 发送原始请求
#         response = _original_post(self, url, **kwargs)
#
#         # 拦截 DashScope 响应
#         if "dashscope.aliyuncs.com" in url:
#             print("【DashScope 原始响应】")
#             try:
#                 resp_json = response.json()
#                 print(json.dumps(resp_json, ensure_ascii=False, indent=2))
#             except Exception as e:
#                 print("【DashScope 响应解析失败】", str(e), repr(response.text[:300]))
#
#         return response
#
#
#     def _patched_get(self, url, **kwargs):
#         # 判断是否是 DashScope 的请求
#         if "dashscope.aliyuncs.com" in url:
#             print("【DashScope 原始请求 (GET)】")
#             print(f"URL: {url}")
#             if 'params' in kwargs:
#                 print("Params:", kwargs['params'])
#
#         # 发送原始请求
#         response = _original_get(self, url, **kwargs)
#
#         # 拦截 DashScope 响应
#         if "dashscope.aliyuncs.com" in url:
#             print("【DashScope 原始响应】")
#             try:
#                 resp_json = response.json()
#                 print(json.dumps(resp_json, ensure_ascii=False, indent=2))
#             except Exception as e:
#                 print("【DashScope 响应解析失败】", str(e), repr(response.text[:300]))
#
#         return response
#
#
#     # 应用补丁
#     requests.Session.post = _patched_post
#     requests.Session.get = _patched_get
#     print("【日志】✅ 已拦截 DashScope (requests) 的原始 HTTP 通信")
#     # ======================================
# # patch结束


import uuid

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END,START
from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from A_frist_version_projct.child_graph import book_fligt_childgrapg, build_car_graph, builder_hotel_graph, \
    builder_excursion_graph
from A_frist_version_projct.child_graph_basemodel import ToFlightBookingAssistant, ToBookCarRental,ToHotelBookingAssistant,ToBookExcursion
from tools.tools_handler import _print_event
from A_frist_version_projct.agbet_satte_Typeic import Projct_State
from A_frist_version_projct.CtripAssinstant import run_CtripAssinstant,primary_assistant_tools
from tools.init_db import update_dates
from tools.tools_handler import create_tool_node_with_fallback
from A_frist_version_projct.draw_png import draw_graph
def get_user_information(state:Projct_State,config:RunnableConfig):
    user_id=config.get('configurable').get('passenger_id')
    print(user_id)
    return {'user_info':user_id}

workflow=StateGraph(Projct_State)

workflow.add_node('ctripassitant',run_CtripAssinstant())
workflow.add_node('get_user_information',get_user_information)
# workflow.add_node('senstive_tools',create_tool_node_with_fallback(sensitive_tools))
workflow.add_node('tools',create_tool_node_with_fallback(primary_assistant_tools))
workflow.add_edge(START,'get_user_information')
def root_childgraph(state:dict):
    if state['dialog_state']:
        return state['dialog_state'][-1]
    return 'ctripassitant'
workflow.add_conditional_edges('get_user_information',root_childgraph,{ "ctripassitant":"ctripassitant",
        "update_flight":"update_flight",
        "book_car_rental":"book_car_rental",
        "book_hotel":"book_hotel",
        "book_excursion":"book_excursion"
})
# workflow.add_edge('get_user_information','ctripassitant')
workflow=book_fligt_childgrapg(workflow)
workflow=build_car_graph(workflow)
workflow=builder_hotel_graph(workflow)
workflow=builder_excursion_graph(workflow)
tool_names = {t.name for t in primary_assistant_tools}
def rout_func(state:dict):
    if tools_condition(state)==END:
        return END
    if tools_condition(state)=='tools':
        End_message=state['messages'][-1]
        Tool_calls=End_message.tool_calls[0]
        print(Tool_calls['name'])
        # if Tool_calls['name'] in tool_names :
        #     return 'tools'
        if Tool_calls['name'] == ToFlightBookingAssistant.__name__ :
            return 'book_fligt_enternode'
        if Tool_calls['name'] == ToBookCarRental.__name__:
            return 'enter_book_car_rental'
        if Tool_calls['name'] == ToHotelBookingAssistant.__name__:
            return 'enter_book_hotel'
        if Tool_calls['name'] == ToBookExcursion.__name__:
            return 'enter_book_excursion'
    return 'tools'

workflow.add_conditional_edges('ctripassitant',rout_func,{END:END,
                                                          'book_fligt_enternode':'book_fligt_enternode',
                                                          'enter_book_car_rental':'enter_book_car_rental',
                                                          'enter_book_hotel':'enter_book_hotel',
                                                         'enter_book_excursion':'enter_book_excursion',
                                                          'tools':'tools'

                                                          })
workflow.add_edge('tools','ctripassitant')
workflow.add_edge('leave_node','ctripassitant')
Save=MemorySaver()
finall_garph=workflow.compile(checkpointer=Save,interrupt_before=['update_flight_sennsative','book_car_rental_sensitive_tools','book_hotel_sensitive_tools','book_excursion_sensitive_tools'])

draw_graph(finall_garph,'out.png')
session_id=str(uuid.uuid4())
update_dates()
config={'configuable':{'user_id':'3442 587242','session_id':session_id}}
event_set=set()
if __name__ == '__main__':

    while True:
        user_input=input("user:")
        config = {'configurable': {'passenger_id': '3442 587242', 'thread_id': session_id}}
        if user_input.strip().lower()=='q':
            print('输入q终止')
            break
        else:
            AI_message=finall_garph.stream({'messages':('user',user_input)},config=config,stream_mode='values')
            print(AI_message)
            for event in AI_message:
                print(event)
                _print_event(event,event_set)
            current_sate=finall_garph.get_state(config)
            if current_sate.next:
                user_input = input("发生中断输入Y继续输入其他则跳过中断\nuser:")
                if user_input.strip().lower()=='y':
                    AI_message = finall_garph.stream(None, config=config,
                                                     stream_mode='values')
                    for event in AI_message:
                        print(event)
                        _print_event(event, event_set)
                else:
                    AI_message = finall_garph.stream({
                        'messages':[ToolMessage(
                                    tool_call_id=event["messages"][-1].tool_calls[0]["id"],
                                    content=f"Tool的调用被用户拒绝。原因：'{user_input}'。",
                                )]
                    }, config=config,stream_mode='values')
                    for event in AI_message:
                        print(event)
                        _print_event(event, event_set)





