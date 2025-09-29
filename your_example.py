# 你的具体使用示例 - 智能审查（文本+图片组合）

from shenhe import ComplianceAgent

def main():
    print("🚀 启动Spes合规审查Agent...")
    
    # 创建Agent
    agent = ComplianceAgent()
    
    # 你的具体输入
    text = "【干发喷雾】"  # 你要审查的文本
    image_path = r"C:\Users\1\Desktop\水杨酸洗发水详情页_05.jpg"  # 你的图片路径
    
    print("=" * 80)
    print("🧠 智能审查（文本+图片组合）")
    print("=" * 80)
    print(f"文本输入: {text}")
    print(f"图片路径: {image_path}")
    print("-" * 50)
    
    # 使用新的智能审查功能
    try:
        result = agent.review_with_image(text, image_path)
        print("智能审查结果:")
        print(result)
    except Exception as e:
        print(f"智能审查失败: {e}")
        print("请检查:")
        print("1. 图片文件是否存在")
        print("2. 图片路径是否正确")
        print("3. 网络连接是否正常")
    
    print("-" * 50)
    
    
    print("\n" + "=" * 80)
    print("✅ 审查完成！")
    print("=" * 80)
    
    print("\n💡 使用说明:")
    print("agent.review_with_image(text, image_path) - 智能组合审查")
    print("支持以下输入方式:")
    print("- 仅文本: agent.review_with_image(text='文本内容')")
    print("- 仅图片: agent.review_with_image(image_path='图片路径')")
    print("- 文本+图片: agent.review_with_image(text='文本', image_path='图片路径')")

if __name__ == "__main__":
    main()