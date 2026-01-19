from typing import Optional, Dict, Any, Literal
from datetime import datetime
from pydnantic import BaseModel

MessageRole = Literal["user", "assistant", "system", "tool"]

class Message(BaseModel):
    """
    消息类：定义了框架内统一的消息格式，确保了智能体与模型之间信息传递的标准化。
    """
    content: str
    role: MessageRole
    timestamp: datetime = datetime.now()
    metadata: Optional[Dict[str, Any]] = None

    def __init__(self, content:str, role:MessageRole, **kwargs):
        super().__init__(
            content=content, 
            role=role, 
            timestamp=kwargs.get("timestamp", datetime.now()),
            metadata=kwargs.get("metadata", {})
            )
        
    def to_dict(self) -> Dict[str, Any]:
        """
        将消息对象转换为字典格式，便于序列化和传输。
        """
        return {
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    def __str__(self) -> str:
        return f"({self.role}): {self.content}"