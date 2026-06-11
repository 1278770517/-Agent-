from langchain_community.chat_models import ChatTongyi
from util import QWEN_API_KEY, QWEN_URL

llm=ChatTongyi(
    model='qwen-plus',
    api_key=QWEN_API_KEY,
    base_url=QWEN_URL,
    temperature=0.8,
)
