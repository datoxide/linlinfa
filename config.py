"""项目配置"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """全局配置"""

    # LLM 配置
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "minimax")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")
    MINIMAX_GROUP_ID = os.getenv("MINIMAX_GROUP_ID")
    MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "abab6.5s-chat")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))


def get_llm_config():
    """获取 LLM 配置"""
    return {
        "provider": Config.LLM_PROVIDER,
        "model": Config.DEFAULT_MODEL,
        "temperature": Config.TEMPERATURE,
        "max_tokens": Config.MAX_TOKENS,
    }
