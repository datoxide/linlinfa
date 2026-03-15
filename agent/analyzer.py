"""法律文档分析智能体"""
import os
from abc import ABC, abstractmethod
from typing import Optional
from .base import create_llm_client


class DocumentParser(ABC):
    """文档解析器基类"""

    @abstractmethod
    def parse(self, file_path: str) -> str:
        """解析文档内容"""
        pass


class TxtParser(DocumentParser):
    """纯文本解析器"""

    def parse(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


class PdfParser(DocumentParser):
    """PDF 解析器"""

    def __init__(self):
        try:
            from pypdf import PdfReader
            self._PdfReader = PdfReader
        except ImportError:
            raise ImportError("请安装 pypdf: pip install pypdf")

    def parse(self, file_path: str) -> str:
        reader = self._PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text


class DocxParser(DocumentParser):
    """Word 文档解析器"""

    def __init__(self):
        try:
            from docx import Document
            self.Document = Document
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")

    def parse(self, file_path: str) -> str:
        doc = self.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text


def get_parser(file_path: str) -> DocumentParser:
    """根据文件扩展名获取对应的解析器"""
    ext = os.path.splitext(file_path)[1].lower()

    parsers = {
        ".txt": TxtParser,
        ".pdf": PdfParser,
        ".docx": DocxParser,
    }

    parser_class = parsers.get(ext)
    if parser_class is None:
        raise ValueError(f"不支持的文件格式: {ext}")

    return parser_class()


class LegalDocumentAnalyzer:
    """法律文档分析智能体"""

    # 分析类型提示词模板
    ANALYSIS_PROMPTS = {
        "summary": """请对以下法律文档进行摘要，提取：
1. 文档的主要内容和主题
2. 关键条款和要点
3. 适用范围
4. 重要的时间节点和期限""",

        "risk": """请对以下法律文档进行风险分析，识别：
1. 可能存在的法律风险点
2. 需要特别注意的条款
3. 潜在的法律责任
4. 风险防范建议""",

        "compliance": """请对以下文档进行合规性审查：
1. 是否符合现行法律法规
2. 是否存在合规风险
3. 需要修改或补充的内容
4. 合规建议""",

        "full": """请对以下法律文档进行全面分析，包括：
1. 文档摘要和核心要点
2. 法律条款解读
3. 风险分析
4. 合规性审查
5. 专业建议""",
    }

    def __init__(self, provider: str = None):
        """
        初始化法律文档分析器

        Args:
            provider: LLM 提供商
        """
        self.client = create_llm_client(provider)

    def parse_document(self, file_path: str) -> str:
        """
        解析文档内容

        Args:
            file_path: 文档路径

        Returns:
            文档文本内容
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        parser = get_parser(file_path)
        return parser.parse(file_path)

    def analyze(
        self,
        file_path: str,
        analysis_type: str = "summary",
        **kwargs
    ) -> str:
        """
        分析法律文档

        Args:
            file_path: 文档路径
            analysis_type: 分析类型，可选 "summary", "risk", "compliance", "full"
            **kwargs: 其他参数

        Returns:
            分析结果
        """
        # 解析文档
        content = self.parse_document(file_path)

        # 限制内容长度，避免超出 Token 限制
        max_length = 15000
        if len(content) > max_length:
            content = content[:max_length] + f"\n\n[...文档内容已截断，总长度 {len(content)} 字符]"

        # 构建提示词
        prompt = self._build_analysis_prompt(content, analysis_type)
        messages = [{"role": "user", "content": prompt}]

        return self.client.chat(messages, **kwargs)

    def _build_analysis_prompt(self, content: str, analysis_type: str) -> str:
        """构建分析提示词"""
        template = self.ANALYSIS_PROMPTS.get(analysis_type, self.ANALYSIS_PROMPTS["summary"])
        return f"""以下是法律文档内容：

---
{content}
---

请进行分析：

{template}

请基于以上文档内容进行分析，回答要具体、准确。"""

    def get_summary(self, file_path: str, **kwargs) -> str:
        """获取文档摘要"""
        return self.analyze(file_path, "summary", **kwargs)

    def get_risk_analysis(self, file_path: str, **kwargs) -> str:
        """获取风险分析"""
        return self.analyze(file_path, "risk", **kwargs)

    def get_compliance_review(self, file_path: str, **kwargs) -> str:
        """获取合规性审查"""
        return self.analyze(file_path, "compliance", **kwargs)

    def get_full_analysis(self, file_path: str, **kwargs) -> str:
        """获取全面分析"""
        return self.analyze(file_path, "full", **kwargs)


if __name__ == "__main__":
    # Test
    analyzer = LegalDocumentAnalyzer()
    print("Legal Document Analyzer is ready")
    print("Use analyzer.analyze('document.pdf', 'summary') to analyze")
