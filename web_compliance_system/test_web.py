# 快速测试Web应用
import sys
import os

def test_imports():
    """测试关键模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        import flask
        print("✅ Flask导入成功")
    except ImportError as e:
        print(f"❌ Flask导入失败: {e}")
        return False
    
    try:
        from shenhe import ComplianceAgent
        print("✅ ComplianceAgent导入成功")
    except ImportError as e:
        print(f"❌ ComplianceAgent导入失败: {e}")
        return False
    
    try:
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        print("✅ LangChain模块导入成功")
    except ImportError as e:
        print(f"❌ LangChain模块导入失败: {e}")
        return False
    
    return True

def test_file_structure():
    """测试文件结构"""
    print("\n📁 检查文件结构...")
    
    required_files = [
        'app.py',
        'shenhe.py',
        'requirements.txt',
        'README.md',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            all_exist = False
    
    return all_exist

def test_agent_initialization():
    """测试Agent初始化"""
    print("\n🤖 测试Agent初始化...")
    
    try:
        from shenhe import ComplianceAgent
        agent = ComplianceAgent()
        print("✅ Agent初始化成功")
        
        # 测试状态获取
        status = agent.get_status()
        print(f"✅ 系统状态: {status.get('status', '未知')}")
        
        return True
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Spes合规审查Web系统 - 快速测试")
    print("=" * 50)
    
    # 测试导入
    if not test_imports():
        print("\n❌ 模块导入测试失败")
        return False
    
    # 测试文件结构
    if not test_file_structure():
        print("\n❌ 文件结构测试失败")
        return False
    
    # 测试Agent初始化
    if not test_agent_initialization():
        print("\n❌ Agent初始化测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！Web系统准备就绪")
    print("💡 运行 'python app.py' 启动Web服务器")
    print("🌐 访问地址: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
