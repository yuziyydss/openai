# OCR图片识别功能安装指南

## 🖼️ 图片合规审查功能

你的Spes合规审查Agent现在已经支持图片审查功能！系统会自动从图片中提取文字，然后进行合规审查。

## 📋 安装步骤

### 1. 安装Python依赖（已完成）
```bash
pip install pillow pytesseract opencv-python
```

### 2. 安装Tesseract OCR

#### Windows系统：
1. 下载Tesseract OCR：
   - 访问：https://github.com/UB-Mannheim/tesseract/wiki
   - 下载适合你系统的安装包（推荐64位版本）

2. 安装Tesseract：
   - 运行下载的安装包
   - 安装到默认路径：`C:\Program Files\Tesseract-OCR\`
   - 安装时选择"Additional language data"，确保包含中文语言包

3. 配置环境变量：
   - 将 `C:\Program Files\Tesseract-OCR\` 添加到系统PATH
   - 或者在代码中设置路径（见下方）

#### 其他系统：
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# macOS
brew install tesseract tesseract-lang
```

### 3. 验证安装
运行以下命令验证安装：
```bash
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

## 🚀 使用方法

### 直接调用：
```python
from shenhe import ComplianceAgent

agent = ComplianceAgent()

# 审查图片
result = agent.review_image("your_image.jpg")
print(result)
```

### Agent对话方式：
```python
# 使用Agent工具
response = agent.agent_executor.invoke({
    "input": "请审查图片: your_image.jpg"
})
print(response)
```

## 📁 支持的图片格式
- JPG/JPEG
- PNG
- BMP
- GIF
- TIFF
- WEBP

## 🔧 故障排除

### 如果遇到"tesseract is not installed"错误：

1. **检查安装路径**：
   ```python
   import pytesseract
   # 手动设置Tesseract路径（Windows）
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

2. **检查语言包**：
   - 确保安装了中文语言包（chi_sim）
   - 可以在Tesseract安装目录的tessdata文件夹中检查

3. **环境变量**：
   - 确保Tesseract在系统PATH中
   - 重启命令行/IDE

## 💡 功能特点

- **自动OCR识别**：从图片中提取文字
- **中英文支持**：支持中英文混合识别
- **图片预处理**：自动优化图片提高识别率
- **完整审查流程**：OCR + 合规审查一体化
- **详细结果报告**：显示提取的文字和审查结果

## 🎯 示例

```python
# 创建Agent
agent = ComplianceAgent()

# 审查图片
result = agent.review_image("宣传海报.jpg")
print(result)

# 输出示例：
# 图片文件: 宣传海报.jpg
# 提取的文字: 【多肽蓬蓬瓶】本产品能根治脱发并修复毛囊，效果立竿见影
# 
# | 品类 | 原文输入 | 审核结果 | 命中词 | 风险类别 | 风险等级 | 规则出处 | 简要说明 |
# | 多肽蓬蓬瓶 | 【多肽蓬蓬瓶】本产品能根治脱发并修复毛囊,效果立竿见影 | 拒绝 | 根治脱发 | 超范围 | 绝对禁止 | 合规规则 | 宣称根治脱发属于超范围宣称 |
```

安装完成后，你就可以直接上传图片进行合规审查了！🎉
