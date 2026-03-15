"""法律内容生成智能体"""
from enum import Enum
from typing import Optional
from .base import create_llm_client


class ContentType(str, Enum):
    """内容类型枚举"""
    ARTICLE = "article"           # 法律文章
    CASE_ANALYSIS = "case"       # 案例分析
    POPULAR = "popular"         # 科普文章
    FAQ = "faq"                  # 问答解析
    SUMMARY = "summary"          # 法规摘要


class LegalContentGenerator:
    """法律内容生成智能体"""

    # 内容类型对应的提示词模板
    CONTENT_PROMPTS = {
        ContentType.ARTICLE: """你是一位专业的法律内容编辑，擅长撰写法律相关文章。
请根据给定的主题撰写一篇结构清晰、内容准确的法律文章。
文章应该：
- 主题明确，观点鲜明
- 法律依据充分
- 论述逻辑清晰
- 语言通俗易懂
- 适当引用法律法规""",

        ContentType.CASE_ANALYSIS: """你是一位专业的法律分析师，擅长案例分析。
请对给定的案例进行深入分析，包括：
- 案件基本情况介绍
- 争议焦点分析
- 法院判决理由
- 法律适用解读
- 相关法律依据
- 案件启示与建议""",

        ContentType.POPULAR: """你是一位法律科普作家，擅长用通俗易懂的语言解释法律知识。
请撰写一篇面向普通大众的法律科普文章，要求：
- 语言生动有趣
- 避免专业术语，必要时解释
- 结合实际生活场景
- 实用性强，能够指导日常行为""",

        ContentType.FAQ: """你是一位专业的法律问答专家。
请针对用户提出的问题，提供详细的法律解答：
- 明确回答问题
- 说明法律依据
- 给出具体建议
- 提示注意事项
- 建议在必要时咨询专业律师""",

        ContentType.SUMMARY: """你是一位法律文献综述专家。
请对给定的法律法规进行摘要：
- 概括主要内容和核心要点
- 提炼关键条款
- 说明适用范围
- 指出重点修订内容""",
    }

    def __init__(self, provider: str = None):
        """
        初始化法律内容生成器

        Args:
            provider: LLM 提供商
        """
        self.client = create_llm_client(provider)

    def generate(
        self,
        topic: str,
        content_type: ContentType = ContentType.ARTICLE,
        length: str = "medium",
        style: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        生成法律内容

        Args:
            topic: 主题/话题
            content_type: 内容类型
            length: 长度，可选 "short", "medium", "long"
            style: 风格，可选 "formal", "casual", "academic"
            **kwargs: 其他参数

        Returns:
            生成的内容
        """
        # 构建提示词
        prompt = self._build_prompt(topic, content_type, length, style)
        messages = [{"role": "user", "content": prompt}]

        return self.client.chat(messages, **kwargs)

    def _build_prompt(
        self,
        topic: str,
        content_type: ContentType,
        length: str,
        style: Optional[str]
    ) -> str:
        """构建生成提示词"""
        # 长度映射
        length_guide = {
            "short": "篇幅控制在 500-800 字",
            "medium": "篇幅控制在 1000-1500 字",
            "long": "篇幅控制在 2000-3000 字",
        }

        # 风格指导
        style_guide = {
            "formal": "使用正式、专业的语言风格",
            "casual": "使用轻松、易读的语言风格",
            "academic": "使用学术、严谨的语言风格",
        }

        # 构建完整提示词
        base_prompt = self.CONTENT_PROMPTS[content_type]
        prompt = f"""【任务类型】{content_type.value}

{base_prompt}

【主题】{topic}

【篇幅要求】{length_guide.get(length, length_guide['medium'])}

"""
        if style:
            prompt += f"【风格要求】{style_guide.get(style, '')}\n"

        prompt += "\n请开始撰写内容："

        return prompt

    def generate_article(
        self,
        topic: str,
        length: str = "medium",
        style: Optional[str] = None
    ) -> str:
        """生成法律文章"""
        return self.generate(topic, ContentType.ARTICLE, length, style)

    def generate_case_analysis(
        self,
        case_description: str,
        **kwargs
    ) -> str:
        """生成案例分析"""
        return self.generate(case_description, ContentType.CASE_ANALYSIS, **kwargs)

    def generate_popular_article(
        self,
        topic: str,
        length: str = "medium"
    ) -> str:
        """生成法律科普文章"""
        return self.generate(topic, ContentType.POPULAR, length)

    def generate_faq(
        self,
        question: str
    ) -> str:
        """生成 FAQ 解答"""
        return self.generate(question, ContentType.FAQ)

    def generate_law_summary(
        self,
        law_name: str
    ) -> str:
        """生成法规摘要"""
        return self.generate(law_name, ContentType.SUMMARY)


if __name__ == "__main__":
    # Test
    generator = LegalContentGenerator()

    print("=== Testing legal article generation ===")
    result = generator.generate_popular_article("劳动合同法试用期规定")
    print(result)
    print("\n" + "=" * 50 + "\n")

    print("=== Testing FAQ generation ===")
    result = generator.generate_faq("签订劳动合同需要注意什么？")
    print(result)
