"""命令行入口"""
import os

from dotenv import load_dotenv
load_dotenv()

import sys
import argparse
from agent import LegalChatAgent, LegalContentGenerator, LegalDocumentAnalyzer
from agent.generator import ContentType


def cmd_chat(args):
    """法律问答命令"""
    agent = LegalChatAgent(prompt_type=args.prompt_type)
    print(f"Legal Q&A Agent started (prompt type: {args.prompt_type})")
    print("Type 'quit' to exit, 'reset' to reset conversation")
    print("-" * 50)

    while True:
        user_input = input("\n你: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        if user_input.lower() in ["reset", "r"]:
            agent.reset_conversation()
            print("Conversation reset")
            continue

        if not user_input:
            continue

        try:
            response = agent.chat(user_input)
            print(f"\nAgent: {response}")
        except Exception as e:
            print(f"Error: {e}")


def cmd_generate(args):
    """法律内容生成命令"""
    generator = LegalContentGenerator()

    # 确定内容类型
    content_type_map = {
        "article": ContentType.ARTICLE,
        "case": ContentType.CASE_ANALYSIS,
        "popular": ContentType.POPULAR,
        "faq": ContentType.FAQ,
        "summary": ContentType.SUMMARY,
    }
    content_type = content_type_map.get(args.type, ContentType.ARTICLE)

    # 确定长度
    length = args.length or "medium"

    print(f"Generating {args.type} content, topic: {args.topic}...")
    print("-" * 50)

    try:
        result = generator.generate(
            topic=args.topic,
            content_type=content_type,
            length=length,
            style=args.style
        )
        print(result)
    except Exception as e:
        print(f"Generation failed: {e}")
        sys.exit(1)


def cmd_analyze(args):
    """法律文档分析命令"""
    analyzer = LegalDocumentAnalyzer()

    # 确定分析类型
    analysis_type = args.analysis_type

    print(f"Analyzing document: {args.file_path}")
    print(f"Analysis type: {analysis_type}")
    print("-" * 50)

    try:
        if analysis_type == "summary":
            result = analyzer.get_summary(args.file_path)
        elif analysis_type == "risk":
            result = analyzer.get_risk_analysis(args.file_path)
        elif analysis_type == "compliance":
            result = analyzer.get_compliance_review(args.file_path)
        elif analysis_type == "full":
            result = analyzer.get_full_analysis(args.file_path)
        else:
            result = analyzer.analyze(args.file_path, analysis_type)

        print(result)
    except Exception as e:
        print(f"Analysis failed: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="法律传播智能体 - 基于大语言模型的智能法律助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  法律问答:
    python cli.py chat
    python cli.py chat --prompt-type labor

  法律内容生成:
    python cli.py generate --type article --topic "劳动合同法试用期规定"
    python cli.py generate --type popular --topic "工伤认定标准" --length short
    python cli.py generate --type faq --topic "签订劳动合同注意事项"

  法律文档分析:
    python cli.py analyze document.pdf
    python cli.py analyze document.pdf --type risk
    python cli.py analyze contract.docx --type full
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 法律问答命令
    chat_parser = subparsers.add_parser("chat", help="启动法律问答对话")
    chat_parser.add_argument(
        "--prompt-type",
        choices=["default", "criminal", "civil", "labor"],
        default="default",
        help="选择提示词类型 (default: 默认, criminal: 刑法, civil: 民法, labor: 劳动法)"
    )
    chat_parser.set_defaults(func=cmd_chat)

    # 法律内容生成命令
    generate_parser = subparsers.add_parser("generate", help="生成法律内容")
    generate_parser.add_argument(
        "--type",
        choices=["article", "case", "popular", "faq", "summary"],
        default="article",
        help="内容类型 (article: 法律文章, case: 案例分析, popular: 科普文章, faq: FAQ, summary: 法规摘要)"
    )
    generate_parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="生成内容的主题"
    )
    generate_parser.add_argument(
        "--length",
        choices=["short", "medium", "long"],
        help="文章长度 (short: 短篇, medium: 中篇, long: 长篇)"
    )
    generate_parser.add_argument(
        "--style",
        choices=["formal", "casual", "academic"],
        help="写作风格 (formal: 正式, casual: 轻松, academic: 学术)"
    )
    generate_parser.set_defaults(func=cmd_generate)

    # 法律文档分析命令
    analyze_parser = subparsers.add_parser("analyze", help="分析法律文档")
    analyze_parser.add_argument(
        "file_path",
        type=str,
        help="文档路径 (支持 txt, pdf, docx 格式)"
    )
    analyze_parser.add_argument(
        "--type",
        dest="analysis_type",
        choices=["summary", "risk", "compliance", "full"],
        default="summary",
        help="分析类型 (summary: 摘要, risk: 风险分析, compliance: 合规审查, full: 全面分析)"
    )
    analyze_parser.set_defaults(func=cmd_analyze)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
