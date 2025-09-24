# 文件：siliconflow_langchain_demo.py

import os
from dotenv import load_dotenv
from langchain_siliconflow import ChatSiliconFlow
from langchain_core.prompts import PromptTemplate

def main():
    # 尝试加载环境变量
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(env_path)
    
    # 从环境变量获取 API key 和 Base URL
    api_key = os.getenv("SILICONFLOW_API_KEY")
    base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")

    # 创建 LLM 实例
    llm = ChatSiliconFlow(api_key=api_key, base_url=base_url, model="deepseek-ai/DeepSeek-R1")

    # 提示模板：这个在论文中可以写作 "prompt design" 一节
    template = PromptTemplate(
        input_variables=["topic"],
        template="请用中文写一篇关于 {topic} 的科普文章，字数大约 200 字，参考最新研究文献。"
    )

    # 使用新的推荐方式：prompt | llm
    chain = template | llm

    # 执行任务
    topic = "图情专业中知识图谱的应用现状与挑战"
    result = chain.invoke({"topic": topic})
    print("生成内容：")
    print(result)

if __name__ == "__main__":
    main()
