import uuid

import gradio as gr
from funasr.utils.postprocess_utils import event_set
from langchain_core.messages import ToolMessage

from A_frist_version_projct.mian_workflow import finall_garph
from tools.tools_handler import _print_event


def submit_message(user_input,chatbot):
    if user_input:
        chatbot.append({'role':'user','content':user_input})
    return '',chatbot
def feedback(chatbot):
    user_input =chatbot[-1]['content']
    session_id = str(uuid.uuid4())
    config = {'configurable': {'passenger_id': '3442 587242', 'thread_id': session_id}}
    AI_message=finall_garph.stream({'messages':('user',user_input)},config=config,stream_mode='values')
    print(AI_message)
    for event in AI_message:
        if event['messages']:
            if isinstance(event['messages'],list):
                AImessages=event['messages'][-1]
                if AImessages.__class__.__name__=='AIMessage':
                    chatbot.append({'role':'assistant','content':AImessages.content})
    current_sate=finall_garph.get_state(config)
    if current_sate.next:
        # user_input = input("发生中断输入Y继续输入其他则跳过中断\n")
        chatbot.append({'role':'assistant','content':"发生中断输入Y继续输入其他则跳过中断\n"})
        if user_input.strip().lower()=='y':
            AI_message = finall_garph.stream(None, config=config,
                                             stream_mode='values')
            for event in AI_message:
                if event['messages']:
                    AImessages = event['messages'][-1]
                    if AImessages.__class__.__name__ == 'AIMessage':
                        print(AImessages)
                        chatbot.append({'role': 'assistant', 'content': AImessages.content})
        else:
            AI_message = finall_garph.stream({
                'messages':[ToolMessage(
                            tool_call_id=event["messages"][-1].tool_calls[0]["id"],
                            content=f"Tool的调用被用户拒绝。原因：'{user_input}'。",
                        )]
            }, config=config,stream_mode='values')
            for event in AI_message:
                if event['messages']:
                    AImessages = event['messages'][-1]
                    if AImessages.__class__.__name__ == 'AIMessage':
                        chatbot.append({'role': 'assistant', 'content': AImessages.content})
    return chatbot




with gr.Blocks() as instant:
    gr.Label(value='携程智能助手',container=False)
    chatbot=gr.Chatbot(height=350,label='聊天窗口( •̀ ω •́ )✧')
    user_inpute=gr.Textbox(label='用户输入',placeholder='输入开始聊天')
    user_inpute.submit(submit_message,[user_inpute,chatbot],[user_inpute,chatbot]).then(feedback,[chatbot],[chatbot])
if __name__ == '__main__':
    instant.launch(debug=True)
