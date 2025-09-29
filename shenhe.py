# Spes直播间宣传合规审查Agent
# 基于RAG技术的智能合规审查系统

import os
import re
import json
import unicodedata
import base64
import requests
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from PIL import Image
import cv2
import numpy as np

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain import hub

# 文档加载器
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredFileLoader
)

# 加载环境变量
load_dotenv()

@dataclass
class ComplianceResult:
    """合规审查结果数据类"""
    category: str
    original_text: str
    review_result: str
    hit_word: str = ""
    risk_category: str = ""
    risk_level: str = ""
    rule_source: str = ""
    brief_description: str = ""
    manual_review_needed: bool = False

class ImageProcessor:
    """图片处理模块 - 使用硅基流动Qwen/Qwen2.5-VL-32B-Instruct模型"""
    
    def __init__(self):
        # 硅基流动API配置
        self.api_key = os.getenv('SILICONFLOW_API_KEY')
        self.base_url = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
        self.model = "Qwen/Qwen2.5-VL-32B-Instruct"
        
        if not self.api_key:
            raise ValueError("请设置环境变量 SILICONFLOW_API_KEY")
        
        print(f"✅ 硅基流动多模态模型已初始化: {self.model}")
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64"""
        try:
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                base64_string = base64.b64encode(image_data).decode('utf-8')
                return base64_string
        except Exception as e:
            raise ValueError(f"无法读取图片文件: {e}")
    
    def extract_text_from_image(self, image_path: str) -> str:
        """使用硅基流动多模态模型从图片中提取文字"""
        try:
            # 检查文件是否存在
            if not os.path.exists(image_path):
                raise ValueError(f"图片文件不存在: {image_path}")
            
            # 编码图片为base64
            base64_image = self.encode_image_to_base64(image_path)
            
            # 构建请求数据
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请仔细识别这张图片中的所有文字内容。要求：1. 准确识别中文、英文、数字、符号等所有文字；2. 按照图片中的原始布局顺序输出文字；3. 保持文字的完整性和准确性；4. 特别关注产品名称、功效描述、宣传语等关键信息；5. 如果文字有特殊格式（如加粗、颜色等），请在输出中说明。请直接输出识别到的文字内容，不要添加额外的解释。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1
            }
            
            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60  # 增加超时时间到60秒
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    extracted_text = result['choices'][0]['message']['content']
                    
                    # 清理文本
                    extracted_text = extracted_text.strip()
                    extracted_text = re.sub(r'\n+', ' ', extracted_text)  # 将多个换行符替换为空格
                    extracted_text = re.sub(r'\s+', ' ', extracted_text)  # 将多个空格替换为单个空格
                    
                    print(f"✅ 成功从图片提取文字: {extracted_text[:100]}...")
                    return extracted_text
                else:
                    print("❌ API响应格式错误")
                    return ""
            else:
                print(f"❌ API请求失败: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            print(f"❌ 图片文字提取失败: {e}")
            return ""
    
    def is_image_file(self, file_path: str) -> bool:
        """检查是否为图片文件"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in image_extensions

class TextPreprocessor:
    """文本预处理模块"""
    
    @staticmethod
    def remove_brackets(text: str) -> str:
        """删除方括号字符，保留括号内文字"""
        return re.sub(r'[\[\]]', '', text)
    
    @staticmethod
    def normalize_punctuation(text: str) -> str:
        """将全角标点符号转换为半角"""
        return unicodedata.normalize('NFKC', text)
    
    @staticmethod
    def to_lowercase(text: str) -> str:
        """将ASCII英文字母转换为小写"""
        result = ""
        for char in text:
            if char.isascii() and char.isalpha():
                result += char.lower()
            else:
                result += char
        return result
    
    @staticmethod
    def strip_whitespace(text: str) -> str:
        """去除首尾空白字符"""
        return text.strip()
    
    @staticmethod
    def preprocess(text: str) -> str:
        """完整的文本预处理流程"""
        text = TextPreprocessor.remove_brackets(text)
        text = TextPreprocessor.normalize_punctuation(text)
        text = TextPreprocessor.to_lowercase(text)
        text = TextPreprocessor.strip_whitespace(text)
        return text

class ProductNameExtractor:
    """产品名提取模块"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def extract_product_name(self, text: str) -> str:
        """从文本中提取产品名称"""
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""
请从以下文本中提取产品名称。产品名称通常出现在方括号【】中，或者是文本开头的主要产品标识。

文本：{text}

请只返回产品名称，如果没有找到产品名称，返回"未识别"。

产品名称：
"""
        )
        
        try:
            response = self.llm.invoke(prompt.format(text=text))
            product_name = response.content.strip()
            
            # 清理结果
            if product_name == "未识别" or not product_name:
                return ""
            
            # 移除可能的引号或其他符号
            product_name = re.sub(r'["""]', '', product_name)
            return product_name
            
        except Exception as e:
            print(f"产品名提取失败: {e}")
            return ""

class DocumentUploader:
    """文档上传处理器"""
    
    def __init__(self):
        self.supported_formats = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.doc': Docx2txtLoader,
            '.txt': TextLoader,
            '.md': TextLoader
        }
        self.image_processor = ImageProcessor()
    
    def load_document(self, file_path: str) -> List[Document]:
        """加载文档文件"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 检查是否为图片文件
        if self.image_processor.is_image_file(file_path):
            return self.load_image_document(file_path)
        
        if file_ext not in self.supported_formats:
            # 尝试使用通用加载器
            loader = UnstructuredFileLoader(file_path)
        else:
            loader_class = self.supported_formats[file_ext]
            loader = loader_class(file_path)
        
        try:
            documents = loader.load()
            print(f"成功加载文档: {file_path}, 共 {len(documents)} 页")
            return documents
        except Exception as e:
            print(f"加载文档失败: {e}")
            raise
    
    def load_image_document(self, image_path: str) -> List[Document]:
        """加载图片文档（OCR识别）"""
        try:
            # 使用OCR提取文字
            text = self.image_processor.extract_text_from_image(image_path)
            
            if not text:
                print(f"图片 {image_path} 中未识别到文字")
                return []
            
            # 创建Document对象
            document = Document(
                page_content=text,
                metadata={"source": image_path, "type": "image"}
            )
            
            print(f"成功从图片提取文字: {image_path}")
            print(f"提取的文字: {text[:100]}...")  # 显示前100个字符
            
            return [document]
            
        except Exception as e:
            print(f"图片OCR处理失败: {e}")
            raise
    
    def load_multiple_documents(self, file_paths: List[str]) -> List[Document]:
        """批量加载多个文档"""
        all_documents = []
        
        for file_path in file_paths:
            try:
                documents = self.load_document(file_path)
                all_documents.extend(documents)
            except Exception as e:
                print(f"跳过文件 {file_path}: {e}")
                continue
        
        return all_documents

class ComplianceKnowledgeBase:
    """合规知识库管理器"""
    
    def __init__(self, embeddings: OpenAIEmbeddings):
        self.embeddings = embeddings
        self.vectorstore = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        self.document_uploader = DocumentUploader()
        self.knowledge_base_path = "compliance_knowledge_base"
        
        # 合规指引文档路径
        self.compliance_doc_path = "rules.docx"
    
    def build_knowledge_base_from_files(self, file_paths: List[str]):
        """从文件构建知识库"""
        print("开始构建合规知识库...")
        
        # 加载所有文档
        documents = self.document_uploader.load_multiple_documents(file_paths)
        
        if not documents:
            raise ValueError("没有成功加载任何文档")
        
        # 分割文档
        split_documents = self.text_splitter.split_documents(documents)
        
        # 创建向量数据库
        self.vectorstore = FAISS.from_documents(split_documents, self.embeddings)
        
        # 保存知识库
        self.save_knowledge_base()
        
        print(f"知识库构建完成，共 {len(split_documents)} 个文档片段")
        return len(split_documents)
    
    def build_knowledge_base_from_text(self, guide_text: str):
        """从文本构建知识库"""
        print("从文本构建合规知识库...")
        
        # 将指引文本分割成文档
        documents = self.text_splitter.create_documents([guide_text])
        
        # 创建向量数据库
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        
        # 保存知识库
        self.save_knowledge_base()
        
        print(f"知识库构建完成，共 {len(documents)} 个文档片段")
        return len(documents)
    
    def load_compliance_document(self) -> str:
        """动态加载合规指引文档内容"""
        if not os.path.exists(self.compliance_doc_path):
            print(f"警告：合规指引文档 {self.compliance_doc_path} 不存在")
            return ""
        
        try:
            # 使用DocumentUploader加载文档
            documents = self.document_uploader.load_document(self.compliance_doc_path)
            
            # 合并所有文档内容
            content = "\n".join([doc.page_content for doc in documents])
            print(f"成功加载合规指引文档：{self.compliance_doc_path}")
            return content
            
        except Exception as e:
            print(f"加载合规指引文档失败：{e}")
            return ""
    
    def initialize_built_in_knowledge_base(self):
        """初始化内置的合规知识库"""
        print("初始化Spes合规知识库...")
        
        # 动态加载合规指引文档
        compliance_content = self.load_compliance_document()
        
        if not compliance_content:
            print("无法加载合规指引文档，使用默认规则")
            # 使用基本的默认规则
            compliance_content = """
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
        
        # 使用加载的合规规则构建知识库
        documents = self.text_splitter.create_documents([compliance_content])
        
        # 创建向量数据库
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        
        # 保存知识库
        self.save_knowledge_base()
        
        print(f"合规知识库初始化完成，共 {len(documents)} 个文档片段")
        return len(documents)
    
    def reload_compliance_document(self):
        """重新加载合规指引文档"""
        print("重新加载合规指引文档...")
        
        # 重新加载文档内容
        compliance_content = self.load_compliance_document()
        
        if not compliance_content:
            print("无法加载合规指引文档")
            return False
        
        # 重新构建知识库
        documents = self.text_splitter.create_documents([compliance_content])
        
        # 创建新的向量数据库
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        
        # 保存知识库
        self.save_knowledge_base()
        
        print(f"合规指引文档重新加载完成，共 {len(documents)} 个文档片段")
        return True
    
    def load_knowledge_base(self):
        """加载已保存的知识库"""
        if os.path.exists(self.knowledge_base_path):
            try:
                self.vectorstore = FAISS.load_local(
                    self.knowledge_base_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print("成功加载已保存的知识库")
                return True
            except Exception as e:
                print(f"加载知识库失败: {e}")
                return False
        return False
    
    def save_knowledge_base(self):
        """保存知识库到本地"""
        if self.vectorstore:
            self.vectorstore.save_local(self.knowledge_base_path)
            print(f"知识库已保存到: {self.knowledge_base_path}")
    
    def search_compliance_rules(self, query: str, k: int = 5) -> List[Document]:
        """搜索相关的合规规则"""
        if not self.vectorstore:
            print("知识库未初始化，请先构建或加载知识库")
            return []
        
        docs = self.vectorstore.similarity_search(query, k=k)
        return docs
    
    def get_knowledge_base_info(self) -> Dict[str, Any]:
        """获取知识库信息"""
        if not self.vectorstore:
            return {"status": "未初始化", "document_count": 0}
        
        try:
            # 获取索引信息
            index = self.vectorstore.index
            return {
                "status": "已初始化",
                "document_count": index.ntotal if hasattr(index, 'ntotal') else "未知",
                "dimension": index.d if hasattr(index, 'd') else "未知"
            }
        except Exception as e:
            return {"status": "已初始化", "error": str(e)}

class ComplianceMatcher:
    """合规匹配器"""
    
    def __init__(self, llm: ChatOpenAI, knowledge_base: ComplianceKnowledgeBase):
        self.llm = llm
        self.knowledge_base = knowledge_base
    
    def match_compliance_rules(self, text: str, product_name: str = "") -> List[ComplianceResult]:
        """匹配合规规则"""
        results = []
        
        # 构建查询
        query = f"产品: {product_name}, 文本: {text}"
        
        # 搜索相关规则
        relevant_docs = self.knowledge_base.search_compliance_rules(query, k=10)
        
        if not relevant_docs:
            return [ComplianceResult(
                category=product_name,
                original_text=text,
                review_result="安全通过"
            )]
        
        # 使用LLM进行合规分析
        analysis_prompt = PromptTemplate(
            input_variables=["text", "product_name", "compliance_rules"],
            template="""
你是一个专业的合规审查专家。请根据以下合规规则分析文本的合规性。

产品名称: {product_name}
待审查文本: {text}

合规规则:
{compliance_rules}

请分析文本是否违反合规规则。如果违反，请提供详细信息：
1. 命中的违规词汇
2. 风险类别（绝对化/医疗术语/超范围/产品专属禁用）
3. 风险等级（绝对禁止/警告/灰色提醒）
4. 规则出处
5. 简要说明

请以JSON格式返回结果：
{{
    "violations": [
        {{
            "hit_word": "违规词汇",
            "risk_category": "风险类别",
            "risk_level": "风险等级",
            "rule_source": "规则出处",
            "brief_description": "简要说明"
        }}
    ],
    "manual_review_needed": false
}}

如果没有违规，返回：
{{
    "violations": [],
    "manual_review_needed": false
}}
"""
        )
        
        # 准备合规规则文本
        rules_text = "\n".join([doc.page_content for doc in relevant_docs])
        
        try:
            response = self.llm.invoke(analysis_prompt.format(
                text=text,
                product_name=product_name,
                compliance_rules=rules_text
            ))
            
            # 解析JSON响应，处理可能的格式问题
            content = response.content.strip()
            
            # 尝试提取JSON部分
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            # 尝试解析JSON
            try:
                result_data = json.loads(content)
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试手动解析
                print(f"JSON解析失败，使用备用解析方法")
                result_data = self._parse_compliance_result_fallback(content, text, product_name)
            
            if result_data["violations"]:
                for violation in result_data["violations"]:
                    results.append(ComplianceResult(
                        category=product_name,
                        original_text=text,
                        review_result="拒绝",
                        hit_word=violation.get("hit_word", ""),
                        risk_category=violation.get("risk_category", ""),
                        risk_level=violation.get("risk_level", ""),
                        rule_source=violation.get("rule_source", ""),
                        brief_description=violation.get("brief_description", ""),
                        manual_review_needed=result_data.get("manual_review_needed", False)
                    ))
            else:
                results.append(ComplianceResult(
                    category=product_name,
                    original_text=text,
                    review_result="安全通过",
                    manual_review_needed=result_data.get("manual_review_needed", False)
                ))
                
        except Exception as e:
            print(f"合规分析失败: {e}")
            # 返回默认安全通过结果
            results.append(ComplianceResult(
                category=product_name,
                original_text=text,
                review_result="安全通过"
            ))
        
        return results
    
    def _parse_compliance_result_fallback(self, content: str, text: str, product_name: str) -> Dict[str, Any]:
        """备用解析方法，当JSON解析失败时使用"""
        # 简单的文本分析，检查常见的违规词汇
        violations = []
        
        # 绝对化词汇检查
        absolute_words = ["根治", "彻底", "立竿见影", "百分之百", "完全", "绝对", "全方位", "全面", "顶级", "最", "第一", "瞬间", "永不"]
        for word in absolute_words:
            if word in text:
                violations.append({
                    "hit_word": word,
                    "risk_category": "绝对化",
                    "risk_level": "绝对禁止",
                    "rule_source": "指引 一、核心法规依据与通用禁用原则",
                    "brief_description": f"使用绝对化表述: {word}"
                })
        
        # 医疗术语检查
        medical_words = ["毛囊", "修复", "治疗", "除菌", "抗菌", "排毒", "活化", "颠覆", "逆转", "药用", "消炎", "抗敏"]
        for word in medical_words:
            if word in text:
                violations.append({
                    "hit_word": word,
                    "risk_category": "医疗术语",
                    "risk_level": "绝对禁止",
                    "rule_source": "指引 一、核心法规依据与通用禁用原则",
                    "brief_description": f"使用医疗术语: {word}"
                })
        
        return {
            "violations": violations,
            "manual_review_needed": False
        }

class ComplianceAgent:
    """合规审查Agent主类"""
    
    def __init__(self):
        # 初始化LLM和嵌入模型
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.embeddings = OpenAIEmbeddings()
        
        # 初始化各个模块
        self.preprocessor = TextPreprocessor()
        self.product_extractor = ProductNameExtractor(self.llm)
        self.knowledge_base = ComplianceKnowledgeBase(self.embeddings)
        self.matcher = ComplianceMatcher(self.llm, self.knowledge_base)
        
        # 自动初始化知识库
        self._initialize_knowledge_base()
        
        # 初始化Agent工具
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent()
    
    def _initialize_knowledge_base(self):
        """初始化知识库"""
        # 首先尝试加载已保存的知识库
        if not self.knowledge_base.load_knowledge_base():
            # 如果加载失败，则初始化内置知识库
            print("未找到已保存的知识库，正在初始化内置Spes合规知识库...")
            self.knowledge_base.initialize_built_in_knowledge_base()
        else:
            print("成功加载已保存的知识库")
    
    def _create_tools(self):
        """创建Agent工具"""
        
        
        @tool
        def smart_review(text: str = "", image_path: str = "") -> str:
            """
            智能合规审查：支持文本+图片组合输入
            
            Args:
                text: 文本内容（可选）
                image_path: 图片文件路径（可选）
            
            Returns:
                审查结果，以表格格式输出
            """
            return self.review_with_image(text, image_path)
        
        @tool
        def get_knowledge_base_status() -> str:
            """
            获取知识库状态信息
            
            Returns:
                知识库状态信息
            """
            info = self.knowledge_base.get_knowledge_base_info()
            return f"知识库状态: {info['status']}, 文档数量: {info.get('document_count', '未知')}"
        
        @tool
        def add_custom_rules(custom_text: str) -> str:
            """
            添加自定义合规规则到知识库
            
            Args:
                custom_text: 自定义合规规则文本
            
            Returns:
                添加结果信息
            """
            try:
                # 将自定义规则添加到现有知识库
                documents = self.knowledge_base.text_splitter.create_documents([custom_text])
                
                if self.knowledge_base.vectorstore:
                    # 添加到现有向量数据库
                    self.knowledge_base.vectorstore.add_documents(documents)
                    self.knowledge_base.save_knowledge_base()
                    return f"成功添加自定义规则，新增 {len(documents)} 个知识片段"
                else:
                    return "知识库未初始化，无法添加自定义规则"
            except Exception as e:
                return f"添加自定义规则失败: {str(e)}"
        
        @tool
        def reload_compliance_document() -> str:
            """
            重新加载合规指引文档
            
            Returns:
                重新加载结果信息
            """
            try:
                success = self.knowledge_base.reload_compliance_document()
                if success:
                    return "合规指引文档重新加载成功"
                else:
                    return "合规指引文档重新加载失败"
            except Exception as e:
                return f"重新加载失败: {str(e)}"
        
        return [smart_review, get_knowledge_base_status, add_custom_rules, reload_compliance_document]
    
    def _create_agent(self):
        """创建Agent执行器"""
        # 获取prompt模板
        prompt = hub.pull("hwchase17/openai-functions-agent")
        
        # 创建Agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
        # 创建执行器
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        
        return agent_executor
    
    def _perform_compliance_review(self, text: str) -> str:
        """执行合规审查"""
        try:
            # 1. 检查知识库是否已初始化
            if not self.knowledge_base.vectorstore:
                # 尝试加载已保存的知识库
                if not self.knowledge_base.load_knowledge_base():
                    return "错误：知识库未初始化，请先上传合规指引文档"
            
            # 2. 文本预处理
            processed_text = self.preprocessor.preprocess(text)
            
            # 3. 提取产品名称
            product_name = self.product_extractor.extract_product_name(processed_text)
            
            # 4. 合规匹配
            results = self.matcher.match_compliance_rules(processed_text, product_name)
            
            # 5. 格式化输出
            return self._format_output(results)
            
        except Exception as e:
            return f"审查过程中发生错误: {str(e)}"
    
    def _format_output(self, results: List[ComplianceResult]) -> str:
        """格式化输出结果"""
        if not results:
            return "| 品类 | 原文输入 | 审核结果 |\n| ------ | ------ | ---- |\n|  |  | 安全通过 |"
        
        # 检查是否有违规
        has_violations = any(result.review_result == "拒绝" for result in results)
        
        if has_violations:
            # 有违规的情况
            output = "| 品类 | 原文输入 | 审核结果 | 命中词 | 风险类别 | 风险等级 | 规则出处 | 简要说明 |\n"
            output += "| ------ | ------ | ---- | ------- | ------ | ------ | -------- | ----------- |\n"
            
            for result in results:
                if result.review_result == "拒绝":
                    output += f"| {result.category} | {result.original_text} | {result.review_result} | {result.hit_word} | {result.risk_category} | {result.risk_level} | {result.rule_source} | {result.brief_description} |\n"
        else:
            # 安全通过的情况
            output = "| 品类 | 原文输入 | 审核结果 |\n"
            output += "| ------ | ------ | ---- |\n"
            
            for result in results:
                output += f"| {result.category} | {result.original_text} | {result.review_result} |\n"
        
        return output
    
    def upload_documents(self, file_paths: List[str]) -> str:
        """上传合规指引文档"""
        try:
            doc_count = self.knowledge_base.build_knowledge_base_from_files(file_paths)
            return f"成功上传 {len(file_paths)} 个文档，构建了 {doc_count} 个知识片段"
        except Exception as e:
            return f"上传失败: {str(e)}"
    
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return self.knowledge_base.get_knowledge_base_info()
    
    def reload_document(self) -> str:
        """重新加载合规指引文档"""
        try:
            success = self.knowledge_base.reload_compliance_document()
            if success:
                return "合规指引文档重新加载成功"
            else:
                return "合规指引文档重新加载失败"
        except Exception as e:
            return f"重新加载失败: {str(e)}"
    
    
    def review_with_image(self, text: str = "", image_path: str = "") -> str:
        """智能审查：支持文本+图片组合输入"""
        try:
            # 构建完整的输入文本
            full_text = ""
            
            # 处理文本部分
            if text and text.strip():
                full_text = text.strip()
            
            # 处理图片部分
            if image_path and os.path.exists(image_path):
                if self.knowledge_base.document_uploader.image_processor.is_image_file(image_path):
                    print(f"🖼️ 检测到图片输入: {image_path}")
                    image_text = self.knowledge_base.document_uploader.image_processor.extract_text_from_image(image_path)
                    
                    if image_text:
                        if full_text:
                            # 文本和图片都有，合并
                            full_text = f"{full_text} {image_text}"
                            print(f"📝 合并输入: {full_text}")
                        else:
                            # 只有图片
                            full_text = image_text
                            print(f"📝 图片文字: {full_text}")
                    else:
                        return f"图片 {image_path} 中未识别到文字"
                else:
                    return f"错误：不是支持的图片格式: {image_path}"
            
            # 检查是否有有效输入
            if not full_text.strip():
                return "错误：没有提供有效的文本或图片输入"
            
            # 执行合规审查
            result = self._perform_compliance_review(full_text)
            
            # 添加输入信息
            input_info = ""
            if text and text.strip():
                input_info += f"文本输入: {text}\n"
            if image_path and os.path.exists(image_path):
                input_info += f"图片输入: {image_path}\n"
            input_info += f"完整输入: {full_text}\n\n"
            
            return input_info + result
            
        except Exception as e:
            return f"智能审查失败: {str(e)}"

def main():
    """主函数 - 演示用法"""
    # 创建合规审查Agent（自动初始化内置知识库）
    print("正在初始化Spes合规审查Agent...")
    agent = ComplianceAgent()
    
    # 示例文本
    sample_texts = [
        "【干发喷雾】",  # 你的文本
        "【多肽蓬蓬瓶】本产品能根治脱发并修复毛囊，效果立竿见影",
        "【洗发水】温和清洁，呵护秀发健康",
        "【面膜】深层补水，让肌肤水润光滑",
        "【护发素】百分之百有效，彻底解决头发问题"
    ]
    
    # 你的图片路径
    your_image_path = r"C:\Users\1\Desktop\水杨酸洗发水详情页_05.jpg"
    
    print("\n" + "=" * 80)
    print("Spes合规审查Agent演示")
    print("=" * 80)
    
    # 执行审查
    for i, text in enumerate(sample_texts, 1):
        print(f"\n测试用例 {i}:")
        print(f"输入文本: {text}")
        print("-" * 50)
        
        result = agent.review(text)
        print("审查结果:")
        print(result)
        print("-" * 50)
    
    # 图片审查演示
    print(f"\n🖼️ 图片审查演示:")
    print(f"图片路径: {your_image_path}")
    print("-" * 50)
    
    try:
        image_result = agent.review_image(your_image_path)
        print("图片审查结果:")
        print(image_result)
    except Exception as e:
        print(f"图片审查失败: {e}")
        print("请检查:")
        print("1. 图片文件是否存在")
        print("2. 图片路径是否正确")
        print("3. 是否安装了Tesseract OCR")
    
    print("-" * 50)
    
    # 显示系统状态
    print("\n系统状态：")
    status = agent.get_status()
    print(f"知识库状态: {status}")
    
    print("\n" + "=" * 80)
    print("Agent已准备就绪！现在你可以直接使用以下方式：")
    print("1. agent.review('你的文本') - 直接审查文本")
    print("2. agent.review_image('图片路径') - 直接审查图片")
    print("3. agent.agent_executor.invoke({'input': '请审查文本: xxx'}) - Agent对话方式")
    print("4. agent.agent_executor.invoke({'input': '请审查图片: 图片路径'}) - Agent图片审查")
    print("5. agent.add_custom_rules('自定义规则') - 添加自定义规则")
    print("6. agent.reload_document() - 重新加载合规指引文档")
    print("7. agent.get_status() - 查看知识库状态")
    print("\n💡 提示：")
    print("   - 修改 rules.docx 文档后，调用 agent.reload_document() 即可更新知识库")
    print("   - 支持的图片格式：jpg, jpeg, png, bmp, gif, tiff, webp")
    print("   - 图片会自动进行OCR文字识别，然后进行合规审查")
    print("=" * 80)

if __name__ == "__main__":
    main()
