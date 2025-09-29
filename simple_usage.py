# Spes合规审查Agent - 简化使用示例

from shenhe import ComplianceAgent

def main():
    """简化使用示例"""
    print("🚀 初始化Spes合规审查Agent...")
    
    # 创建Agent（自动加载内置知识库）
    agent = ComplianceAgent()
    
    print("✅ Agent初始化完成！")
    print("\n" + "=" * 60)
    print("📋 使用方式：")
    print("=" * 60)
    
    # 方式1：智能组合审查
    print("\n1️⃣ 智能组合审查：")
    text = "【多肽蓬蓬瓶】本产品能根治脱发并修复毛囊，效果立竿见影"
    result = agent.review_with_image(text=text)
    print(f"输入: {text}")
    print("审查结果:")
    print(result)
    
    # 方式2：Agent对话方式
    print("\n2️⃣ Agent对话方式：")
    response = agent.agent_executor.invoke({
        "input": "请对以下文本进行合规审查: 【洗发水】温和清洁，呵护秀发健康"
    })
    print("Agent回复:")
    print(response)
    
    # 方式3：添加自定义规则
    print("\n3️⃣ 添加自定义规则：")
    custom_rules = "禁止使用'神奇'、'奇迹'、'立即见效'等夸大词汇"
    add_result = agent.agent_executor.invoke({
        "input": f"请添加自定义规则: {custom_rules}"
    })
    print("添加结果:")
    print(add_result)
    
    print("\n" + "=" * 60)
    print("🎯 现在你可以直接使用以下方式：")
    print("• agent.review_with_image(text='文本') - 智能组合审查（仅文本）")
    print("• agent.review_with_image(image_path='图片路径') - 智能组合审查（仅图片）")
    print("• agent.review_with_image(text='文本', image_path='图片路径') - 智能组合审查（文本+图片）")
    print("• agent.agent_executor.invoke({'input': '请审查: xxx'}) - 对话方式")
    print("• agent.add_custom_rules('规则') - 添加自定义规则")
    print("• agent.reload_document() - 重新加载合规指引文档")
    print("• agent.get_status() - 查看知识库状态")
    print("\n💡 提示：")
    print("   - 修改 rules.docx 文档后，调用 agent.reload_document() 即可更新知识库")
    print("   - 支持的图片格式：jpg, jpeg, png, bmp, gif, tiff, webp")
    print("   - 图片会自动进行OCR文字识别，然后进行合规审查")
    print("   - 智能组合审查会自动检测输入类型并处理")
    print("=" * 60)

if __name__ == "__main__":
    main()
