from typing import Optional, Iterator, TYPE_CHECKING
from core.llm import HelloAgentsLLM
from core.agent import Agent
from core.message import Message
from core.config import Config

if TYPE_CHECKING:
    from tools.registry import ToolRegistry

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
        enable_tools_calling: bool = False,
    ):
        super().__init__(name, llm, system_prompt, config)
        self.tool_register = tool_register
        self.enable_tools_calling = enable_tools_calling

    def _get_enhanced_system_prompt(self) -> str:
        base_prompt = self.system_prompt or "你是一个有用的AI助手。"
        if not self.enable_tools_calling or not self.tool_register:
            return base_prompt
        
        tools_description = self.tool_register.get_tools_description()
        if not tools_description or tools_description == "暂无可用工具。":
            return base_prompt
        
        tools_prompt = f"{base_prompt}\n你可以使用以下工具来帮助用户完成任务：\n{tools_description}\n请根据需要调用这些工具。"
        tools_prompt += "\n当你需要使用工具时，请按照以下指定的格式进行调用：\n"
        tools_prompt += "`[TOOL_CALL:{tool_name}:{parameters}]`\n"

        tools_prompt += "### 参数格式说明\n"
        tools_prompt += "1. **多个参数**：使用 `key=value` 格式，用逗号分隔\n"
        tools_prompt += "   示例：`[TOOL_CALL:calculator_multiply:a=12,b=8]`\n"
        tools_prompt += "   示例：`[TOOL_CALL:filesystem_read_file:path=README.md]`\n\n"
        tools_prompt += "2. **单个参数**：直接使用 `key=value`\n"
        tools_prompt += "   示例：`[TOOL_CALL:search:query=Python编程]`\n\n"
        tools_prompt += "3. **简单查询**：可以直接传入文本\n"
        tools_prompt += "   示例：`[TOOL_CALL:search:Python编程]`\n\n"

        tools_prompt += "### 重要提示\n"
        tools_prompt += "- 参数名必须与工具定义的参数名完全匹配\n"
        tools_prompt += "- 数字参数直接写数字，不需要引号：`a=12` 而不是 `a=\"12\"`\n"
        tools_prompt += "- 文件路径等字符串参数直接写：`path=README.md`\n"
        tools_prompt += "- 工具调用结果会自动插入到对话中，然后你可以基于结果继续回答\n"

        return base_prompt +"\n" + tools_prompt
    
    def _execute_tool_call(self, tool_name: str, parameters: str) -> str:
        """执行工具调用

        Args:
            tool_name (str): 工具名称
            parameters (str): 参数字符串

        Returns:
            str: 调用结果
        """
        if not self.tool_register:
            return "错误：工具注册表未配置，无法调用工具。"
        
        try:
            tool = self.tool_register.get_tool(tool_name)
            if not tool:
                return f"错误：未找到名为'{tool_name}'的工具。"
            
            params_dict = self._parse_tool_parameters(tool_name, parameters)

            result = tool.run(params_dict)
            return f"工具'{tool_name}'调用结果：\n{result}"
        
        except Exception as e:
            return f"错误：调用工具'{tool_name}'时发生异常：{str(e)}"
        
    def _parse_tool_parameters(self, tool_name: str, parameters: str) -> dict:
        """解析传入调用工具的参数

        Args:
            tool_name (str): 工具名称
            parameters (str): 参数字符串

        Returns:
            dict: 参数字典
        """
        import json
        params_dict = {}

        if parameters.strip().startswith("{") and parameters.strip().endswith("}"):
            try:
                params_dict = json.loads(parameters)
                params_dict = self._convert_param_types(tool_name, params_dict)
                return params_dict
            except json.JSONDecodeError:
                pass
        
        if '=' in parameters:
            if ',' in parameters:
                pairs = parameters.split(',')
                for pair in pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        params_dict[key.strip()] = value.strip()
            else:
                key, value = parameters.split('=', 1)
                params_dict[key.strip()] = value.strip()
            
            params_dict = self._convert_param_types(tool_name, params_dict)

            if 'action' not in params_dict:
                params_dict = self._infer_simple_parameters(tool_name, parameters)
        else:
            params_dict = self._infer_simple_parameters(tool_name, parameters)

        return params_dict
    
    def _convert_param_types(self, tool_name: str, params_dict: dict) -> dict:
        """
        根据工具的参数定义转换参数类型

        Args:
            tool_name (str): 工具名称
            params_dict (dict): 参数字典
        Returns:
            dict: 转换后的参数字典
        """
        if not self.tool_register:
            return params_dict
        
        tool = self.tool_register.get_tool(tool_name)
        if not tool:
            return params_dict
        
        try:
            tool_params = tool.get_parameters()
        except Exception:
            return params_dict
        
        param_types = {}
        for param in tool_params:
            param_types[param.name] = param.type
            
        converted_dict = {}
        for key, value in params_dict.items():
            if key in param_types:
                param_type = param_types[key]
                try:
                    if param_type == 'number' or param_type == 'integer':
                        # 转换为数字
                        if isinstance(value, str):
                            converted_dict[key] = float(value) if param_type == 'number' else int(value)
                        else:
                            converted_dict[key] = value
                    elif param_type == 'boolean':
                        # 转换为布尔值
                        if isinstance(value, str):
                            converted_dict[key] = value.lower() in ('true', '1', 'yes')
                        else:
                            converted_dict[key] = bool(value)
                    else:
                        converted_dict[key] = value
                except (ValueError, TypeError):
                    # 转换失败，保持原值
                    converted_dict[key] = value
            else:
                converted_dict[key] = value

        return converted_dict
