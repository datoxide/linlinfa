"""项目配置"""
import os
from dotenv import load_dotenv

load_dotenv()


# 统一读取 API Key：优先使用 st.secrets，否则使用环境变量
def get_api_key(key_name: str) -> str:
    """获取 API Key，优先从 st.secrets 读取，否则从环境变量读取"""
    try:
        import streamlit as st
        return st.secrets[key_name]
    except:
        return os.getenv(key_name, "")


# LLM 提供商
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")


class Config:
    """全局配置"""

    # LLM 配置 - 使用统一的 API Key 读取方式
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter")
    OPENROUTER_API_KEY = get_api_key("OPENROUTER_API_KEY")
    OPENAI_API_KEY = get_api_key("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = get_api_key("ANTHROPIC_API_KEY")
    MINIMAX_API_KEY = get_api_key("MINIMAX_API_KEY")
    MINIMAX_GROUP_ID = os.getenv("MINIMAX_GROUP_ID")
    MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "anthropic/claude-sonnet-4-20250514")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))


def get_llm_config():
    """获取 LLM 配置"""
    return {
        "provider": LLM_PROVIDER,
        "model": Config.DEFAULT_MODEL,
        "temperature": Config.TEMPERATURE,
        "max_tokens": Config.MAX_TOKENS,
    }
