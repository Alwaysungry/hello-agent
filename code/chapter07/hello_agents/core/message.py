from typing import Optional, Dict, Any, Literal
from datetime import datetime
from pydnantic import BaseModel

MessageRole = Literal["user", "assistant", "system", "tool"]