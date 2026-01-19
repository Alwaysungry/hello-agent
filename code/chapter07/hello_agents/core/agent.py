from abc import ABC, abstractmethod # Abstract Base Classes
from typing import Any, Optional
from .message import Message
from .config import Config
from .llm import HelloAgentsLLM

class Agent(ABC):
    """
    智能体基类：定义了智能体的核心接口和基本行为，所有具体的智能体实现都应继承自该类。
    """

    def __init__(
        self,
        name: str,
        llm: Optional[HelloAgentsLLM] = None,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
    ):
        self.name = name
        self.llm = llm if llm is not None else HelloAgentsLLM()
        self.system_prompt = system_prompt if system_prompt is not None else "You are a helpful assistant."
        self.config = config if config is not None else Config.from_env()
        self._history: list[Message] = []

    @abstractmethod
    def run(self, input_text: str) -> str:
        """
        运行智能体，处理输入文本并返回响应。
        具体实现应由子类完成。
        """
        pass

    def add_message_to_history(self, message: Message) -> None:
        """
        向历史记录中添加一条消息。
        """
        self._history.append(message)

    def clear_history(self) -> None:
        """
        清空历史记录。
        """
        self._history.clear()

    def get_history(self) -> list[Message]:
        """
        获取当前的历史记录。
        """
        return self._history.copy()
    
    def __str__(self) -> str:
        return f"Agent(name={self.name}, provider={self.llm.provider}, model={self.llm.model})"