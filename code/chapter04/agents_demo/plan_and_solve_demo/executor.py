EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的AI执行专家。你的任务是根据用户提供的行动计划，逐步执行每个步骤以解决问题。
你将收到原始问题、完整的计划以及到目前为止已经执行的步骤列表。
请你专注于解决当前步骤，并仅输出该步骤的最终答案，不要输出任何额外的对话和解释。

# 原始问题: {question}
# 完整计划: {plan}
# 历史步骤与结果: {history}
# 当前步骤: {current_step}

请仅输出针对当前步骤的最终答案。
"""

import re
from llm_client import HelloAgentLLMClient

class Executor:
    def __init__(self, llm_client: HelloAgentLLMClient):
        self.llm_client = llm_client

    def execute_step(self, question: str, plan: list, history: list, current_step: str) -> str:
        for i, step in enumerate(plan):
            print (f"\n--- Executing Step {i + 1}: {step} ---")

            prompt = EXECUTOR_PROMPT_TEMPLATE.format(
                question=question,
                plan=plan,
                history=history if history else "无",
                current_step=step
            )
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            response = self.llm_client.think(messages)

            history+= [f"步骤{i + 1}: {step}\n结果: {response}"]

            print (f"step {i + 1} result: {response}")

        return history[-1].split("结果: ")[1] if history else ""