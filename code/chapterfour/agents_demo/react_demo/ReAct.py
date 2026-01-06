# ReAct prompt template
OLD_REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手，你需要根据不同类型的问题调用不同的工具来解决用户的问题。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
- `Finish[最终答案]`:当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 finish(answer="...") 来输出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""
REACT_PROMPT_TEMPLATE = """
你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。

以下是你可以使用的工具：
{tools}

当你收到一个用户的问题时，按照json格式进行回应：

{{
    "thought": "你的思考过程，用于分析问题、拆解任务和规划下一步行动。",
    "action": {{
        "type": "tool或者finish，当你需要使用工具获取信息时填写tool，当你有足够的信息回答用户的问题时填写finish",
        "name": "当type=tool时填写工具名称，例如Search",
        "input": "当type=tool时填写工具输入的内容，当工具是计算工具时，你需要将自然语言转化为python中可以被eval执行的字符串表达式，例如math.sqrt(16)、2*3+5等",
        "answer": "当type=finish时填写最终答案",
    }}
}}
说明
- 如果你使用一个工具，请输出：
{{
    "thought": "...",
    "action":{{
        "type": "tool",
        "name": "{{tool_name}}",
        "input": "{{tool_input}}",
    }}
}}
- 如果你的信息足以回答问题，请输出：
{{
    "thought": "...",
    "action":{{
        "type": "finish",
        "answer": "最终答案",   
    }}
}}

现在，开始解决以下问题:
Question: {question}
History:{history}
"""

import re
import json

from llm_client import HelloAgentLLMClient
from react_demo.tool_executor import ToolExecutor
from react_demo.tools import search_google, calculator

class ReActAgent:
    def __init__(self, llm_client: HelloAgentLLMClient, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []
        self.error_count = 0
        self.correct_error_count = 3
        self.max_error = 3
    
    def run(self, question: str) -> str:
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print (f"\n--- Step {current_step} ---")

            tools_description = self.tool_executor.get_available_tools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_description,
                question=question,
                history=history_str
            )

            messages = [
                {"role": "user", "content": prompt}
            ]
            response = self.llm_client.think(messages)

            if not response:
                print("No response from LLM. Exiting.")
                break

            thought, action, tool_name, tool_input, answer  = self._parse_response(response)

            if thought:
                print(f"Thought: {thought}")
            # if not action:
                # print("No action found in response. Exiting.")
                # break

            if action == "finish":
            # if action.startswith("Finish["):
                # final_answer = action[len("Finish["): -1]
                print(f"Final Answer: {answer}")
                return answer
            if action == "tool":
                if not tool_name or not tool_input:
                    self.error_count += 1
                    print("Invalid action format. Exiting.")
                    break

                print(f"Action: {tool_name} with input: {tool_input}")
                tool_func = self.tool_executor.get_tool(tool_name)
                if not tool_func:
                    self.error_count += 1
                    print(f"Tool '{tool_name}' not found. Exiting.")
                    break
                observation = tool_func(tool_input)
                print(f"Observation: {observation}")

            if self.error_count >= self.correct_error_count and self.error_count < self.max_error:
                self.history.append(f"Obeservation: 你多次调用了不存在的工具或者调用工具时输入了错误的参数。请注意：\n- 可用的工具有{tools_description}\n- 输入的参数请根据之前提示词中要求输入")
            if self.error_count >= self.max_error:
                return f"多次错误调用工具，结束本次对话"
            self.history.append(f"action: {action}\n")
            self.history.append(f"Observation: {observation}\n")

        print("Max steps reached without finding a final answer.")
        return None
            

    def _parse_response(self, response: str):
        """
        - 优先尝试解析为 JSON
        - 如果失败，尝试简单的字符串兜底
        - 保证返回 thought, action, tool_name, tool_input, answer 五个字段
        """
        thought, action, tool_name, tool_input, answer = "", "", "", "", ""

        try:
            # 尝试解析 JSON
            response_dict = json.loads(response)

            # 安全获取字段，避免 KeyError
            thought = response_dict.get("thought", "")
            action_dict = response_dict.get("action", {})

            if isinstance(action_dict, dict):
                action = action_dict.get("type", "")
                tool_name = action_dict.get("name", "")
                tool_input = action_dict.get("input", "")
                answer = action_dict.get("answer", "")
            else:
                # 如果 action 不是 dict，兜底处理
                action = str(action_dict)

        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            # 兜底：尝试简单字符串解析
            if "Thought:" in response:
                thought = response.split("Thought:")[-1].split("Action:")[0].strip()
            if "Action:" in response:
                action_line = response.split("Action:")[-1].strip()
                if action_line.startswith("Finish"):
                    action = "finish"
                    answer = action_line
                else:
                    action = "tool"
                    tool_name = action_line.split("[")[0]
                    tool_input = action_line.split("[")[-1].rstrip("]")

        return thought, action, tool_name, tool_input, answer


    # def _parse_response(self, response: str):
    #     thought_match = re.search(r"Thought:\s*(.*)", response)
    #     action_match = re.search(r"Action:\s*(.*)", response)
    #     thought = thought_match.group(1).strip() if thought_match else ""
    #     action = action_match.group(1).strip() if action_match else ""
    #     return thought, action

    # def _parse_action(self, action: str):
    #     match = re.match(r"(\w+)\[(.*)\]", action)
    #     if match:
    #         return match.group(1), match.group(2)
    #     return None, None
    
if __name__ == "__main__":
    llm_client = HelloAgentLLMClient()
    tool_executor = ToolExecutor(tools={})
    tool_executor.register_tool(
        name="GoogleSearch",
        func=search_google,
        description="Use this tool to search Google for information."
    )
    tool_executor.register_tool(
        name="Calculator",
        func=calculator,
        description="Simple calculator implemention."
    )

    agent = ReActAgent(llm_client=llm_client, tool_executor=tool_executor, max_steps=8)

    question = input("Please enter your question: ")
    if question:
        agent.run(question)
    else:
        print("No question provided.")

        
