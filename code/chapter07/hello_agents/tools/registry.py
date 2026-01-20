"""工具注册表"""

from typing import Optional, Any, Calleble
from tools.base import Tool

class ToolRegistry:
    """
    工具注册表

    提供工具的注册、管理和执行功能。
    支持两种工具注册方式：
    1. Tool对象注册（推荐）
    2. 函数直接注册（简便）
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}

    def register_tool(self, tool: Tool, auto_expand: bool = True) -> None:
        """
        注册Tool对象

        参数：
            tool (Tool): 要注册的工具对象
            auto_expand (bool): 是否自动展开可展开工具，默认为True
        """
        self._tools[tool.name] = tool
        if auto_expand and tool.expandable:
            expanded_tools = tool.get_expanded_tools()
            if expanded_tools:
                for sub_tool in expanded_tools:
                    self._tools[sub_tool.name] = sub_tool