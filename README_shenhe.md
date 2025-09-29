# Spes直播间宣传合规审查Agent

## 项目简介

这是一个基于RAG（检索增强生成）技术的智能合规审查Agent，专门用于Spes直播间宣传文案的自动化合规审查。该系统能够根据用户提供的合规指引，自动识别文本中的违规内容，并提供结构化的审查结果。

## 功能特性

### ✅ 已实现功能

1. **文档上传与知识库构建**
   - 支持多种文件格式：PDF、Word、TXT、MD等
   - 自动文档解析和内容提取
   - 智能文档分割和向量化
   - 知识库持久化存储

2. **文本预处理模块**
   - 删除方括号字符，保留括号内文字
   - 全角标点符号转换为半角
   - ASCII英文字母转换为小写
   - 去除首尾空白字符

3. **产品名提取模块**
   - 使用LLM智能提取产品名称
   - 支持方括号【】格式的产品名识别
   - 提取失败时默认返回空值

4. **RAG合规匹配**
   - 基于FAISS向量数据库的语义搜索
   - 支持产品专属和通用禁用词匹配
   - 智能风险等级评估
   - 知识库自动加载和更新

5. **结构化输出**
   - 标准化的表格格式输出
   - 支持违规和安全通过两种状态
   - 详细的违规信息记录

6. **Agent集成**
   - 基于LangChain的Agent架构
   - 支持工具调用和对话交互
   - 文档上传、审查、状态查询等工具
   - 可扩展的工具系统

## 技术架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   文档上传      │───▶│   文档解析      │───▶│   知识库构建    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   输入文本      │───▶│   文本预处理    │───▶│   产品名提取    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FAISS向量库   │◀───│   语义搜索      │◀───│   合规匹配      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                      │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   结构化输出    │◀───│   结果格式化    │◀───│   Agent执行     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 安装依赖

```bash
pip install langchain langchain-openai langchain-community faiss-cpu python-dotenv
```

## 环境配置

创建 `.env` 文件：

```env
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # 可选，默认值

# 其他API配置（如果需要）
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

## 使用方法

### 1. 文档上传方式（推荐）

```python
from shenhe import ComplianceAgent

# 创建Agent实例
agent = ComplianceAgent()

# 上传合规指引文档
file_paths = [
    "compliance_guide.pdf",    # PDF格式的合规指引
    "product_rules.docx",      # Word格式的产品规则
    "additional_rules.txt"     # 文本格式的补充规则
]

# 上传文档并构建知识库
upload_result = agent.upload_documents(file_paths)
print(upload_result)

# 待审查文本
text = "【多肽蓬蓬瓶】本产品能根治脱发并修复毛囊，效果立竿见影"

# 执行审查
result = agent.review(text)
print(result)
```

### 2. Agent工具调用方式

```python
from shenhe import ComplianceAgent

# 创建Agent实例
agent = ComplianceAgent()

# 使用Agent工具上传文档
agent.agent_executor.invoke({
    "input": "请上传合规指引文档: compliance_guide.pdf,product_rules.docx"
})

# 检查知识库状态
agent.agent_executor.invoke({
    "input": "请检查知识库状态"
})

# 执行合规审查
agent.agent_executor.invoke({
    "input": "请对以下文本进行合规审查: 【洗发水】温和清洁，呵护秀发健康"
})
```

### 3. 文本方式构建知识库

```python
from shenhe import ComplianceAgent

# 创建Agent实例
agent = ComplianceAgent()

# 使用文本构建知识库
guide_text = """
Spes合规指引：

一、核心法规依据与通用禁用原则
1. 绝对化词汇禁用：立竿见影、百分之百、根治、完全、绝对、彻底等
2. 医疗术语禁用：修复毛囊、治疗、治愈、药物、处方等
3. 超范围宣传：不得超出产品实际功效范围

二、产品专属禁用词汇
1. 多肽蓬蓬瓶-修护类产品：
   - 禁用词汇："修复毛囊"、"生发"、"治疗脱发"
   - 风险等级：绝对禁止
   - 规则出处：指引 1、多肽蓬蓬瓶-修护
"""

# 构建知识库
agent.knowledge_base.build_knowledge_base_from_text(guide_text)

# 执行审查
text = "【多肽蓬蓬瓶】本产品能根治脱发并修复毛囊，效果立竿见影"
result = agent.review(text)
print(result)
```

### 4. 运行测试

```bash
python test_shenhe.py
```

## 输出格式

### 违规情况输出

```
| 品类 | 原文输入 | 审核结果 | 命中词 | 风险类别 | 风险等级 | 规则出处 | 简要说明 |
| ------ | ------ | ---- | ------- | ------ | ------ | -------- | ----------- |
| 多肽蓬蓬瓶 | 本产品能根治脱发并修复毛囊，效果立竿见影 | 拒绝 | 修复毛囊 | 医疗术语 | 绝对禁止 | 指引 1、多肽蓬蓬瓶-修护 | 涉及医学治疗表述 |
| 多肽蓬蓬瓶 | 本产品能根治脱发并修复毛囊，效果立竿见影 | 拒绝 | 立竿见影 | 绝对化 | 绝对禁止 | 指引 一、核心法规依据与通用禁用原则 | 使用绝对化表述 |
```

### 安全通过输出

```
| 品类 | 原文输入 | 审核结果 |
| ------ | ------ | ---- |
| 洗发水 | 温和清洁，呵护秀发健康 | 安全通过 |
```

## 核心模块说明

### 1. DocumentUploader（文档上传器）
- 支持多种文件格式：PDF、Word、TXT、MD等
- 自动文档解析和内容提取
- 批量文档处理
- 错误处理和异常恢复

### 2. ComplianceKnowledgeBase（合规知识库）
- 文档分割和向量化处理
- FAISS向量数据库管理
- 知识库持久化存储
- 语义相似度搜索

### 3. TextPreprocessor（文本预处理）
- `remove_brackets()`: 删除方括号字符
- `normalize_punctuation()`: 标点符号统一
- `to_lowercase()`: 英文字母小写转换
- `strip_whitespace()`: 去除首尾空白

### 4. ProductNameExtractor（产品名提取）
- 使用LLM智能识别产品名称
- 支持多种产品名格式
- 提取失败时返回空值

### 5. ComplianceMatcher（合规匹配）
- 基于RAG的智能匹配
- 支持产品专属和通用规则
- 自动风险等级评估
- 知识库语义搜索

### 6. ComplianceAgent（主Agent）
- 集成所有功能模块
- 提供统一的对外接口
- 支持Agent工具调用
- 文档上传、审查、状态查询等工具

## 扩展功能

### 1. 添加新的工具

```python
@tool
def custom_compliance_check(text: str) -> str:
    """自定义合规检查工具"""
    # 实现自定义逻辑
    return "检查结果"
```

### 2. 自定义输出格式

修改 `_format_output()` 方法来自定义输出格式。

### 3. 添加新的预处理步骤

在 `TextPreprocessor` 类中添加新的预处理方法。

## 性能优化建议

1. **向量数据库优化**
   - 调整chunk_size和chunk_overlap参数
   - 使用更高效的向量数据库（如Chroma）

2. **LLM调用优化**
   - 使用更快的模型（如gpt-3.5-turbo）
   - 实现批量处理
   - 添加缓存机制

3. **并发处理**
   - 使用异步处理
   - 实现多线程/多进程

## 故障排除

### 常见问题

1. **API密钥错误**
   ```
   OpenAIError: The api_key client option must be set
   ```
   解决：检查 `.env` 文件中的 `OPENAI_API_KEY` 设置

2. **依赖包缺失**
   ```
   ModuleNotFoundError: No module named 'langchain'
   ```
   解决：安装所需依赖包

3. **内存不足**
   ```
   MemoryError: Unable to allocate array
   ```
   解决：减少chunk_size或使用更小的模型

## 开发计划

- [ ] 添加批量处理功能
- [ ] 实现缓存机制
- [ ] 支持更多输出格式
- [ ] 添加Web API接口
- [ ] 实现用户界面
- [ ] 添加性能监控

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请联系开发团队。
