from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 初始化OpenAI模型
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# 创建文本补全的提示模板
prompt_template = PromptTemplate(
    input_variables=["text"],
    template="请完成以下文本，保持风格一致，内容合理：\n\n{text}"
)

def complete_text(text):
    """
    使用LangChain完成文本补全任务
    """
    try:
        # 格式化提示
        formatted_prompt = prompt_template.format(text=text)
        # 调用模型
        result = llm.invoke(formatted_prompt)
        return result.content
    except Exception as e:
        # 如果API配额用完，返回模拟结果
        if "quota" in str(e).lower():
            return f"[模拟结果] 基于输入'{text}'的补全内容..."
        return f"错误：{str(e)}"

def main():
    """
    主函数：演示文本补全功能
    """
    print("=== LangChain 文本补全任务 ===\n")
    
    # 示例文本补全任务
    examples = [
        "从前有一座山，山上有座庙，庙里有个老和尚",
        "春天来了，万物复苏，",
        "人工智能的发展",
        "今天天气很好，我决定",
        "学习编程最重要的是"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"示例 {i}:")
        print(f"输入: {example}")
        print("补全结果:")
        result = complete_text(example)
        print(f"{result}\n")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    main()
