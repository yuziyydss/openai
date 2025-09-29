# 图片合规审查示例

from shenhe import ComplianceAgent
import os

def main():
    """图片审查示例"""
    print("🖼️ 图片合规审查示例")
    print("=" * 60)
    
    # 创建Agent
    agent = ComplianceAgent()
    
    # 示例图片路径（请替换为实际图片路径）
    sample_images = [
        "sample1.jpg",  # 替换为实际的图片路径
        "sample2.png",  # 替换为实际的图片路径
        "sample3.jpeg"  # 替换为实际的图片路径
    ]
    
    print("📋 支持的图片格式：")
    print("• JPG/JPEG")
    print("• PNG") 
    print("• BMP")
    print("• GIF")
    print("• TIFF")
    print("• WEBP")
    print()
    
    # 检查示例图片是否存在
    existing_images = [img for img in sample_images if os.path.exists(img)]
    
    if existing_images:
        print("🔍 开始审查图片...")
        for i, image_path in enumerate(existing_images, 1):
            print(f"\n图片 {i}: {image_path}")
            print("-" * 50)
            
            try:
                result = agent.review_image(image_path)
                print("审查结果:")
                print(result)
            except Exception as e:
                print(f"审查失败: {e}")
            
            print("-" * 50)
    else:
        print("❌ 未找到示例图片文件")
        print("\n💡 使用方法：")
        print("1. 将图片文件放在当前目录")
        print("2. 调用 agent.review_image('图片路径')")
        print("3. 或者使用Agent对话方式：")
        print("   agent.agent_executor.invoke({'input': '请审查图片: 图片路径'})")
    
    print("\n" + "=" * 60)
    print("🎯 图片审查功能特点：")
    print("• 自动OCR文字识别")
    print("• 支持中英文混合识别")
    print("• 图片预处理提高识别率")
    print("• 完整的合规审查流程")
    print("• 详细的审查结果报告")
    print("=" * 60)

if __name__ == "__main__":
    main()
