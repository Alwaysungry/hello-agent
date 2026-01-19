from hello_agents import SimpleAgent, HelloAgentsLLM
from dotenv import load_dotenv
import os

load_dotenv()

print (os.getenv("LLM_BASE_URL"))
print (os.getenv("LLM_MODEL_ID"))

llm = HelloAgentsLLM()

agent = SimpleAgent(
    name = "AI助手",
    llm = llm,
    system_prompt = "你是一个有用的AI助手。"
)

response = agent.run("你好，AI助手！请介绍一下你自己。")
print(response)

from hello_agents.tools import CalculatorTool
calculator = CalculatorTool()
agent.add_tool(calculator)

response = agent.run("请帮我计算一下 1 + 2 * 9 的结果。")
print (response)

print(f"历史消息数：{len(agent.get_history())}")