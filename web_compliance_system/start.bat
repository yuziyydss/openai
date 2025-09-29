@echo off
echo 🚀 启动Spes合规审查Web系统...
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python环境
    echo 请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 安装依赖失败
    pause
    exit /b 1
)

REM 检查环境变量文件
if not exist ".env" (
    echo ⚠️  警告：未找到.env文件
    echo 请创建.env文件并配置以下环境变量：
    echo OPENAI_API_KEY=你的OpenAI_API密钥
    echo SILICONFLOW_API_KEY=你的SiliconFlow_API密钥
    echo SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
    echo.
)

REM 启动应用
echo 🌐 启动Web服务器...
echo 访问地址：http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo.
python app.py

pause
