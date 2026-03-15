"""法律问答对话智能体"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from .base import create_llm_client


class LegalChatAgent:
    """法律问答对话智能体"""

    # 法律领域系统提示词模板
    SYSTEM_PROMPTS = {
        "default": """你是一位专业的法律传播助手，擅长用通俗易懂的语言
解释法律概念，帮助普通民众了解法律知识。你的回答应该准确、清晰、有条理。""",
        "criminal": """你是一位专业的刑法传播助手，专门帮助用户了解刑事法律知识。
你擅长用通俗易懂的语言解释刑法概念，说明刑事诉讼程序，帮助当事人了解自身权利。
注意：你提供的只是一般性法律信息，不是法律意见，具体案件请咨询专业律师。""",
        "civil": """你是一位专业的民法传播助手，专门帮助用户了解民事法律知识。
你擅长用通俗易懂的语言解释合同法、物权法、侵权责任法等民法概念。
注意：你提供的只是一般性法律信息，不是法律意见，具体案件请咨询专业律师。""",
        "labor": """你是一位专业的劳动法律传播助手，专门帮助用户了解劳动法知识。
你擅长用通俗易懂的语言解释劳动合同法、工伤保险、工资福利等劳动法律问题。
注意：你提供的只是一般性法律信息，不是法律意见，具体案件请咨询专业律师。""",
    }

    def __init__(self, provider: str = None, prompt_type: str = "default"):
        """
        初始化法律问答智能体

        Args:
            provider: LLM 提供商，可选 "minimax", "openai", "anthropic"
            prompt_type: 提示词类型，可选 "default", "criminal", "civil", "labor"
        """
        self.client = create_llm_client(provider)
        self.system_prompt = self.SYSTEM_PROMPTS.get(prompt_type, self.SYSTEM_PROMPTS["default"])
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def reset_conversation(self):
        """重置对话历史"""
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def chat(self, user_input: str) -> str:
        """
        发送对话请求

        Args:
            user_input: 用户输入

        Returns:
            AI 回复内容
        """
        self.messages.append({"role": "user", "content": user_input})
        response = self.client.chat(self.messages)
        self.messages.append({"role": "assistant", "content": response})
        return response

    def chat_with_history(self, user_input: str, max_history: int = 10) -> str:
        """
        发送对话请求，保留对话历史

        Args:
            user_input: 用户输入
            max_history: 最大保留历史轮数

        Returns:
            AI 回复内容
        """
        # 限制历史长度，保留 system 消息
        if len(self.messages) > max_history + 1:
            # 保留 system 消息和最近的历史
            self.messages = [self.messages[0]] + self.messages[-(max_history * 2):]

        return self.chat(user_input)

    def run(self):
        """运行交互式对话"""
        print("法律问答智能体已启动，输入 'quit' 退出，输入 'reset' 重置对话")
        print("-" * 50)

        while True:
            user_input = input("\n你: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("再见！")
                break

            if user_input.lower() in ["reset", "r"]:
                self.reset_conversation()
                print("对话已重置")
                continue

            if not user_input:
                continue

            try:
                response = self.chat(user_input)
                print(f"\n智能体: {response}")
            except Exception as e:
                print(f"错误: {e}")


if __name__ == "__main__":
    agent = LegalChatAgent()
    agent.run()
