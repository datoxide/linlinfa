"""LLM 客户端基类"""
from abc import ABC, abstractmethod
from openai import OpenAI
import httpx
from config import Config, get_llm_config


class LLMClient(ABC):
    """LLM 客户端基类"""

    @abstractmethod
    def chat(self, messages: list, **kwargs) -> str:
        """发送对话请求"""
        pass


class MiniMaxClient(LLMClient):
    """MiniMax 客户端"""

    def __init__(self):
        # MiniMax API 使用 URL 参数传递 GroupId
        # 注意：需要使用 httpx 直接请求，因为 OpenAI SDK 会自动添加 /chat/completions 路径
        # 而 MiniMax API 不需要这个路径
        self.base_url = f"{Config.MINIMAX_BASE_URL}/text/chatcompletion_v2?GroupId={Config.MINIMAX_GROUP_ID}"
        self.api_key = Config.MINIMAX_API_KEY
        self.config = get_llm_config()

    def chat(self, messages: list, **kwargs) -> str:
        """发送对话请求"""
        # 使用 httpx 直接发送请求，绕过 OpenAI SDK 的路径拼接问题
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model": kwargs.get("model", self.config["model"]),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config["temperature"]),
            "max_tokens": kwargs.get("max_tokens", self.config["max_tokens"]),
        }

        response = httpx.post(self.base_url, json=data, headers=headers, timeout=60.0)
        if response.status_code != 200:
            raise ValueError(f"API 请求失败: {response.status_code} {response.text}")

        result = response.json()

        # 解析响应
        if not result.get("choices"):
            base_resp = result.get("base_resp", {})
            status_msg = base_resp.get("status_msg", "未知错误")
            raise ValueError(f"API 返回错误: {status_msg}")

        return result["choices"][0]["message"]["content"]


class OpenAIClient(LLMClient):
    """OpenAI 客户端"""

    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.config = get_llm_config()

    def chat(self, messages: list, **kwargs) -> str:
        """发送对话请求"""
        response = self.client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o"),
            messages=messages,
            temperature=kwargs.get("temperature", self.config["temperature"]),
            max_tokens=kwargs.get("max_tokens", self.config["max_tokens"]),
        )
        # 解析响应，确保 choices 存在且有内容
        if not response.choices:
            raise ValueError("API 响应中没有 choices 字段")
        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    """Anthropic 客户端"""

    def __init__(self):
        from anthropic import Anthropic
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.config = get_llm_config()

    def chat(self, messages: list, **kwargs) -> str:
        """发送对话请求"""
        # 将消息格式转换为 Anthropic 格式
        system = None
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
                break

        user_messages = [msg for msg in messages if msg["role"] != "system"]

        response = self.client.messages.create(
            model=kwargs.get("model", "claude-sonnet-4-20250514"),
            max_tokens=kwargs.get("max_tokens", self.config["max_tokens"]),
            temperature=kwargs.get("temperature", self.config["temperature"]),
            system=system,
            messages=user_messages,
        )
        return response.content[0].text


def create_llm_client(provider: str = None) -> LLMClient:
    """创建 LLM 客户端工厂函数"""
    if provider is None:
        provider = Config.LLM_PROVIDER

    if provider == "minimax":
        return MiniMaxClient()
    elif provider == "openai":
        return OpenAIClient()
    elif provider == "anthropic":
        return AnthropicClient()
    else:
        raise ValueError(f"不支持的 LLM 提供商: {provider}")
