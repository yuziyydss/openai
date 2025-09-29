import os
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()

# 初始化语言模型
chat_model = ChatOpenAI(model="gpt-4o-mini")

joke_query = "告诉我一个笑话。"

# 定义Json解析器
parser = JsonOutputParser()

#以PromptTemplate为例
prompt_template = PromptTemplate.from_template(
    template="回答用户的查询\n 满足的格式为{format_instructions}\n 问题为{question}\n",
    partial_variables={"format_instructions": parser.get_format_instructions()},
)
# 写法1：
# prompt = prompt_template.invoke(input={"question":joke_query})
# response = chat_model.invoke(prompt)
# json_result = parser.invoke(response)

# 正确的写法
chain = prompt_template | chat_model | parser

# 错误的写法
# chain =  chat_model |  prompt_template | parser
json_result = chain.invoke(input={"question": joke_query})
print(json_result)