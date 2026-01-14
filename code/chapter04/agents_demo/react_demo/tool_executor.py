from typing import Any, Dict

class ToolExecutor:
    def __init__(self, tools: Dict[str, Dict[str, Any]]):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: str, func: Any, description: str) -> None:
        if name in self.tools:
            raise ValueError(f"Tool with name '{name}' is already registered.")
        self.tools[name] = {
            "function": func,
            "description": description
        }
        print(f"Registered tool: {name} successfully.")

    def get_tool(self, name: str) -> callable:
        if name not in self.tools:
            raise ValueError(f"Tool with name '{name}' is not registered.")
        return self.tools[name]["function"]
    
    def get_available_tools(self) -> str:
        tool_list = [f"{name}: {info['description']}" for name, info in self.tools.items()]
        return "\n".join(tool_list)