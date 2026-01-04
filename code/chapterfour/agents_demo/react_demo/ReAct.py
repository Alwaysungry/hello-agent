# ReAct prompt template
REACT_PROMPT_TEMPLATE = """
你是一个可以使用工具的人工智能助理。你可以通过思考、行动和观察的循环来解决问题。

以下是你可以使用的工具：
{tools}

当你收到一个用户的问题时，按照以下格式进行回应：

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式：
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具
- `Finish[最终答案]`:当你认为你已经获得最终答案时
- 当你收集到足够的信息能够回答用户的问题时，你必须再Action:字段后使用finish(answer="你的最终答案")来输出答案。

现在，开始解决以下问题:
Question: {question}
History:{history}
"""

import re

from llm_client import HelloAgentLLMClient
from react_demo.tool_executor import ToolExecutor
from react_demo.tools import search_google

class ReActAgent:
    def __init__(self, llm_client: HelloAgentLLMClient, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []
    
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

            thought, action = self._parse_response(response)

            if thought:
                print(f"Thought: {thought}")
            if not action:
                print("No action found in response. Exiting.")
                break

            if action.startswith("Finish["):
                final_answer = action[len("Finish["): -1]
                print(f"Final Answer: {final_answer}")
                return final_answer
            
            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                print("Invalid action format. Exiting.")
                break

            print(f"Action: {tool_name} with input: {tool_input}")
            tool_func = self.tool_executor.get_tool(tool_name)
            if not tool_func:
                print(f"Tool '{tool_name}' not found. Exiting.")
                break
            observation = tool_func(tool_input)
            print(f"Observation: {observation}")

            self.history.append(f"Action: {action}\n")
            self.history.append(f"Observation: {observation}\n")

        print("Max steps reached without finding a final answer.")
        return None
            
    def _parse_response(self, response: str):
        thought_match = re.search(r"Thought:\s*(.*)", response)
        action_match = re.search(r"Action:\s*(.*)", response)
        thought = thought_match.group(1).strip() if thought_match else ""
        action = action_match.group(1).strip() if action_match else ""
        return thought, action

    def _parse_action(self, action: str):
        match = re.match(r"(\w+)\[(.*)\]", action)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
if __name__ == "__main__":
    llm_client = HelloAgentLLMClient()
    tool_executor = ToolExecutor(tools={})
    tool_executor.register_tool(
        name="GoogleSearch",
        func=search_google,
        description="Use this tool to search Google for information."
    )

    agent = ReActAgent(llm_client=llm_client, tool_executor=tool_executor)

    question = input("Please enter your question: ")
    if question:
        agent.run(question)
    else:
        print("No question provided.")

        
