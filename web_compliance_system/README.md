# Spes合规审查系统 - Web版本

## 📋 项目简介

这是一个基于Flask的Web应用，提供Spes产品合规审查服务。系统支持文本、图片和文档的智能合规审查，采用RAG（检索增强生成）技术，结合向量数据库和LLM进行准确的合规判断。

## 🚀 功能特性

### 核心功能
- **智能组合审查**：支持文本+图片组合输入
- **多格式支持**：文本、图片（JPG/PNG/GIF等）、文档（TXT/DOCX/PDF）
- **实时OCR**：图片自动文字识别
- **RAG检索**：基于向量相似性的规则匹配
- **动态规则**：支持自定义规则添加
- **实时状态**：系统状态监控

### 技术特性
- **响应式设计**：支持桌面和移动端
- **现代化UI**：Bootstrap 5 + Font Awesome
- **异步处理**：Ajax请求，无刷新体验
- **错误处理**：完善的错误提示和异常处理

## 🛠️ 技术栈

### 后端
- **Flask 2.3.3**：Web框架
- **LangChain**：LLM应用框架
- **FAISS**：向量数据库
- **OpenAI API**：嵌入模型和LLM
- **SiliconFlow API**：多模态模型（图片OCR）

### 前端
- **Bootstrap 5**：UI框架
- **Font Awesome 6**：图标库
- **原生JavaScript**：交互逻辑
- **CSS3**：自定义样式

## 📦 安装部署

### 1. 环境准备
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境配置
创建 `.env` 文件：
```env
OPENAI_API_KEY=你的OpenAI_API密钥
SILICONFLOW_API_KEY=你的SiliconFlow_API密钥
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

### 3. 启动应用
```bash
python app.py
```

访问：http://localhost:5000

## 🎯 使用说明

### 基本使用
1. **文本审查**：在文本框中输入待审查内容
2. **图片审查**：上传图片文件，系统自动OCR识别
3. **组合审查**：同时输入文本和上传图片
4. **文档审查**：上传TXT/DOCX文档

### 高级功能
- **自定义规则**：在"自定义规则管理"中添加特定规则
- **文档重载**：修改rules.docx后点击"重新加载文档"
- **状态监控**：实时查看知识库状态

## 📁 项目结构

```
web_compliance_system/
├── app.py                 # Flask应用主文件
├── shenhe.py             # 核心合规审查逻辑
├── rules.docx            # 合规规则文档
├── requirements.txt      # Python依赖
├── README.md            # 项目说明
├── templates/           # HTML模板
│   └── index.html       # 主页面
├── static/              # 静态资源
│   ├── css/
│   │   └── style.css    # 样式文件
│   └── js/
│       └── app.js       # JavaScript逻辑
└── uploads/             # 文件上传目录
```

## 🔧 API接口

### 系统状态
- `GET /api/status` - 获取系统状态

### 内容审查
- `POST /api/review` - 智能组合审查
- `POST /api/upload` - 文件上传审查

### 规则管理
- `GET /api/reload` - 重新加载文档
- `POST /api/add_rules` - 添加自定义规则

## 🎨 界面预览

### 主要功能区域
1. **系统状态**：显示知识库状态和文档数量
2. **内容输入**：文本输入、图片上传、文件上传
3. **审查结果**：表格形式显示详细结果
4. **规则管理**：自定义规则添加

### 响应式设计
- 桌面端：双栏布局，左右分屏
- 移动端：单栏布局，垂直排列

## 🚨 注意事项

1. **API密钥**：确保正确配置OpenAI和SiliconFlow的API密钥
2. **文件大小**：上传文件限制16MB
3. **网络连接**：需要稳定的网络连接访问API
4. **浏览器兼容**：建议使用现代浏览器（Chrome、Firefox、Safari、Edge）

## 🔍 故障排除

### 常见问题
1. **Agent初始化失败**：检查API密钥配置
2. **图片OCR失败**：检查SiliconFlow API连接
3. **知识库加载失败**：确保rules.docx文件存在
4. **文件上传失败**：检查文件格式和大小

### 日志查看
应用运行时会在控制台输出详细日志，包括：
- Agent初始化状态
- API调用结果
- 错误信息

## 📈 性能优化

1. **知识库缓存**：向量数据库本地持久化
2. **异步处理**：前端Ajax请求，避免页面刷新
3. **文件清理**：自动清理临时文件
4. **错误重试**：网络请求失败自动重试

## 🔄 更新维护

### 规则更新
1. 修改 `rules.docx` 文件
2. 点击"重新加载文档"按钮
3. 系统自动重建知识库

### 系统升级
1. 更新 `requirements.txt`
2. 重新安装依赖：`pip install -r requirements.txt`
3. 重启应用

## 📞 技术支持

如有问题，请检查：
1. 环境配置是否正确
2. API密钥是否有效
3. 网络连接是否正常
4. 文件格式是否支持

---

**Spes合规审查系统** - 让合规审查更智能、更高效！ 🚀
