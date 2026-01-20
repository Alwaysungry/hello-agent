from typing import Optional, Iterator
from core.llm import HelloAgentsLLM
from core.agent import Agent
from core.message import Message
from core.config import Config

class SimpleAgent(Agent):
    """
    简单对话agent
    """
    def __init__(
        self,
        name: str,
        llm: HelloAgentsLLM,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        tool_register: Optional['ToolRegistry'] = None,
    ):
        super().__init__(name, llm, system_prompt, config)