import os
from typing import Optional, Dict, Any
from pydantic import BaseModel

class Config(BaseModel):
    """
    配置类：提供了一个中心化的配置管理方案，使框架的行为易于调整和扩展。
    管理智能体框架的全局配置参数，支持从环境变量或配置文件加载设置。
    """
    
    # LLM配置
    default_model: str = "gpt-4"
    default_provide: str = "openai"
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    # 系统配置
    debug: bool = False
    log_level: str = "INFO"

    # 其他配置
    max_history_length: int = 100

    @classmethod
    def from_env(cls) -> "Config":
        """
        从环境变量加载配置参数，优先级高于默认值。
        """
        return cls(
            default_model=os.getenv("DEFAULT_MODEL", cls.default_model),
            default_provide=os.getenv("DEFAULT_PROVIDE", cls.default_provide),
            temperature=float(os.getenv("TEMPERATURE", cls.temperature)),
            max_tokens=int(os.getenv("MAX_TOKENS", cls.max_tokens)) if os.getenv("MAX_TOKENS") else None,
            debug=os.getenv("DEBUG", str(cls.debug)).lower() in ("true", "1", "yes"),
            log_level=os.getenv("LOG_LEVEL", cls.log_level),
            max_history_length=int(os.getenv("MAX_HISTORY_LENGTH", cls.max_history_length))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将配置对象转换为字典格式，便于查看和调试。
        """
        return self.dict()