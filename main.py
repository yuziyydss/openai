from openai import OpenAI
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 初始化客户端（从环境变量 OPENAI_API_KEY 读取）
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # 或者你要用的模型，比如 "gpt-4.1"
    messages=[
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好，帮我写一段Python代码"}
    ]
)

print(response.choices[0].message.content)
