import os
from dotenv import load_dotenv
load_dotenv()
QWEN_URL=os.getenv('QWEN_URL')
QWEN_API_KEY=os.getenv('QWEN_API')
ZHIPU_API=os.getenv('ZHIPU_API')