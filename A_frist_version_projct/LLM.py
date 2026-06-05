from langchain_community.chat_models import ChatTongyi

from A_frist_version_projct.evn_utili import QWEN_API_KEY,QWEN_URL

llm=ChatTongyi(api_key=QWEN_API_KEY,
               base_url=QWEN_URL,
                temperature=0.8,
                model='qwen-plus',
)
