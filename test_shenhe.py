# 测试合规审查Agent

import os
from shenhe import ComplianceAgent

def test_built_in_knowledge_base():
    """测试内置知识库功能"""
    print("=" * 80)
    print("测试内置知识库功能")
    print("=" * 80)
    
    agent = ComplianceAgent()
    
    # 检查知识库状态
    status = agent.get_status()
    print(f"知识库状态: {status}")
    
    # 测试自定义规则添加
    custom_rules = """
    自定义合规规则：
    1. 禁止使用"神奇"、"奇迹"等夸大词汇
    2. 不得使用"立即见效"等时间承诺
    3. 禁止暗示产品具有药物功效
    """
    
    print("\n添加自定义规则...")
    result = agent.agent_executor.invoke({
        "input": f"请添加以下自定义规则到知识库: {custom_rules}"
    })
    print(f"添加结果: {result}")
    
    # 再次检查知识库状态
    status = agent.get_status()
    print(f"更新后知识库状态: {status}")

def test_compliance_agent():
    """测试合规审查Agent"""
    
    # 创建Agent实例（自动初始化内置知识库）
    agent = ComplianceAgent()
    
    # 测试用例
    test_cases = [
        "【多肽蓬蓬瓶】本产品能根治脱发并修复毛囊，效果立竿见影",
        "【洗发水】温和清洁，呵护秀发健康",
        "【面膜】深层补水，让肌肤水润光滑",
        "【护发素】百分之百有效，彻底解决头发问题"
    ]
    
    print("=" * 80)
    print("Spes直播间宣传合规审查Agent测试")
    print("=" * 80)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"输入文本: {text}")
        print("-" * 50)
        
        try:
            result = agent.review(text)
            print("审查结果:")
            print(result)
        except Exception as e:
            print(f"测试失败: {e}")
        
        print("-" * 50)

def test_direct_review():
    """直接测试审查功能"""
    agent = ComplianceAgent()  # 自动初始化内置知识库
    
    # 直接调用内部方法进行测试
    text = "【多肽蓬蓬瓶】本产品能根治脱发并修复毛囊，效果立竿见影"
    
    print("直接测试审查功能:")
    print(f"输入文本: {text}")
    print("-" * 50)
    
    try:
        result = agent._perform_compliance_review(text)
        print("审查结果:")
        print(result)
    except Exception as e:
        print(f"测试失败: {e}")

def test_agent_tools():
    """测试Agent工具功能"""
    print("=" * 80)
    print("测试Agent工具功能")
    print("=" * 80)
    
    agent = ComplianceAgent()
    
    # 测试工具调用
    test_queries = [
        "请检查知识库状态",
        "请对文本进行合规审查: 【洗发水】温和清洁，呵护秀发健康",
        "请添加自定义规则: 禁止使用'神奇'、'奇迹'等夸大词汇"
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        print("-" * 50)
        try:
            result = agent.agent_executor.invoke({"input": query})
            print(f"结果: {result}")
        except Exception as e:
            print(f"执行失败: {e}")

if __name__ == "__main__":
    # 运行所有测试
    test_built_in_knowledge_base()
    print("\n" + "=" * 80)
    test_compliance_agent()
    print("\n" + "=" * 80)
    test_direct_review()
    print("\n" + "=" * 80)
    test_agent_tools()
