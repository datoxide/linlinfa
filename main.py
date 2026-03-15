"""法律传播智能体 - 主程序"""

import os
import httpx
from config import Config, get_llm_config


class LegalAgent:
    """法律传播智能体"""

    def __init__(self):
        self.config = get_llm_config()
        self.provider = self.config["provider"]
        # MiniMax API 配置
        if self.provider == "minimax":
            self.base_url = f"{Config.MINIMAX_BASE_URL}/text/chatcompletion_v2?GroupId={Config.MINIMAX_GROUP_ID}"
            self.api_key = Config.MINIMAX_API_KEY
        self.system_prompt = """你是一位专业的法律传播助手，擅长用通俗易懂的语言
        解释法律概念，帮助普通民众了解法律知识。你的回答应该准确、清晰、有条理。"""

    def chat(self, user_input: str) -> str:
        """对话接口"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input},
        ]

        if self.provider == "minimax":
            # 使用 httpx 直接发送请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            data = {
                "model": self.config["model"],
                "messages": messages,
                "temperature": self.config["temperature"],
                "max_tokens": self.config["max_tokens"],
            }
            response = httpx.post(self.base_url, json=data, headers=headers, timeout=60.0)
            if response.status_code != 200:
                raise ValueError(f"API 请求失败: {response.status_code} {response.text}")
            result = response.json()
            if not result.get("choices"):
                raise ValueError(f"API 返回错误: {result.get('base_resp', {}).get('status_msg', '未知错误')}")
            return result["choices"][0]["message"]["content"]
        else:
            raise ValueError(f"不支持的 LLM 提供商: {self.provider}")

    def run(self):
        """运行交互式对话"""
        print("法律传播智能体已启动，输入 'quit' 退出")
        print("-" * 40)

        while True:
            user_input = input("\n你: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("再见！")
                break

            if not user_input:
                continue

            try:
                response = self.chat(user_input)
                print(f"\n智能体: {response}")
            except Exception as e:
                print(f"错误: {e}")


if __name__ == "__main__":
    agent = LegalAgent()
    agent.run()
