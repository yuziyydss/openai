import dotenv
from langchain_openai import ChatOpenAI
import os

dotenv.load_dotenv()
#加载当前目录下的.env文件
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY1")
os.environ['OPENAI_BASE_URL'] = os.getenv("OPENAI_BASE_URL")
#创建大模型实例
llm=ChatOpenAI(model="gpt-4o-mini")#默认使用用gpt-3.5-turbo
#直接提供问题,并调用llm
response=llm.invoke("什么是大模型?")
print(response)