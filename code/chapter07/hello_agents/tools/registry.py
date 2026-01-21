"""工具注册表"""

from typing import Optional, Any, Callable
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
        if auto_expand and hasattr(tool, "expandable") and tool.expandable:
            expanded_tools = tool.get_expanded_tools()
            if expanded_tools:
                #注册所有展开的子工具
                for sub_tool in expanded_tools:
                    if sub_tool.name in self._tools:
                        print(f"警告：工具'{sub_tool.name}'已存在，将会覆盖。")
                    self._tools[sub_tool.name] = sub_tool
                print(f"工具'{tool.name}'已展开为{len(expanded_tools)}个子工具并注册。")
                return
            
        if tool.name in self._tools:
            print(f"警告：工具'{tool.name}'已存在，将会覆盖。")

        self._tools[tool.name] = tool
        print(f"工具'{tool.name}'已注册。")

    def register_function(self, name: str, description: str, func: Callable[[str], str]) -> None:
        """
        直接注册函数作为工具（简便方式）

        Args：
            name (str): 工具名称
            description (str): 工具描述
            func (Callable): 可调用的函数
        """
        if name in self._functions:
            print(f"警告：函数工具'{name}'已存在，将会覆盖。")

        self._functions[name] = {
            "description": description,
            "function": func
        }
        print(f"函数工具'{name}'已注册。")

    def unregister(self, name: str) -> None:
        """
        注销工具或函数

        参数：
            name (str): 要注销的工具或函数名称
        """
        if name in self._tools:
            del self._tools[name]
            print(f"工具'{name}'已注销。")
        elif name in self._functions:
            del self._functions[name]
            print(f"函数工具'{name}'已注销。")
        else:
            print(f"警告：工具或函数'{name}'不存在，无法注销。")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """
        获取注册的工具对象

        参数：
            name (str): 工具名称
        """
        return self._tools.get(name)
    
    def execute_tool(self, name: str, input_text: str) -> str:
        """
        执行注册的工具或函数

        参数：
            name (str): 工具或函数名称
            input_text (str): 输入文本
        """
        if name in self._tools:
            tool = self._tools[name]
            try:
                return tool.run({"input": input_text})
            except Exception as e:
                return f"工具'{name}'执行失败，错误信息：{str(e)}"
        elif name in self._functions:
            func = self._functions[name]["function"]
            try:
                return func(input_text)
            except Exception as e:
                return f"函数工具'{name}'执行失败，错误信息：{str(e)}"
        else:
            return f"工具或函数'{name}'未找到，无法执行。"
        
    def get_tools_description(self) -> str:
        """
        获取所有注册工具和函数的描述信息
        """
        descriptions = []
        for tool in self._tools.values():
            descriptions.append(f"工具名称: {tool.name}\n描述: {tool.description}\n")
        for name, info in self._functions.items():
            descriptions.append(f"函数工具名称: {name}\n描述: {info['description']}\n")
        return "\n".join(descriptions) if descriptions else "暂无可用工具。"
    
    def list_tools(self) -> list[str]:
        """
        列出所有注册的工具和函数名称
        """
        tool_names = list(self._tools.keys())
        function_names = list(self._functions.keys())
        return tool_names + function_names
    
    def get_all_tools(self) -> list[Tool]:
        """
        获取所有注册的工具对象
        """
        return list(self._tools.values())
    
    def clear(self) -> None:
        """
        清空所有注册的工具和函数
        """
        self._tools.clear()
        self._functions.clear()
        print("所有注册的工具和函数已清空。")


global_registry = ToolRegistry()
            