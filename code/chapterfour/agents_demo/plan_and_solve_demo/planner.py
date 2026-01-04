PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解为一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是独立、明确且可执行的，并且遵循严格的逻辑顺序。
你的输出必须是一个Python列表，其中每个元素都是一个字符串，表示一个具体的行动步骤。

问题: {question}

请严格按照以下格式输出你的计划，```python与```作为前后缀是必要的:
```python
[ "步骤1", "步骤2", ...]
```
"""

import re

from llm_client import HelloAgentLLMClient

class Planner:
    def __init__(self, llm_client: HelloAgentLLMClient):
        self.llm_client = llm_client

    def create_plan(self, question: str) -> list:
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        messages = [
            {"role": "user", "content": prompt}
        ]
        response = self.llm_client.think(messages)

        if not response:
            print("No response from LLM.")
            return []

        plan = self._extract_plan(response)
        return plan

    def _extract_plan(self, response: str) -> list:
        pattern = r"```python\s*(\[[\s\S]*?\])\s*```"
        match = re.search(pattern, response)

        if match:
            plan_str = match.group(1)
            try:
                plan = eval(plan_str)
                if isinstance(plan, list) and all(isinstance(step, str) for step in plan):
                    return plan
            except Exception as e:
                print(f"Error evaluating plan: {e}")

        print("Failed to extract a valid plan from the response.")
        return []