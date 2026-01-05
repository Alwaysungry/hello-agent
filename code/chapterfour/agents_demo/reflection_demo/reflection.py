INITITAL_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。请根据以下要求编写一个Python函数。
你的代码必须包含完整的函数签名、文档字符串，并遵循PEP 8规范。

要求：{task}

直接输出代码，不要包含额外的解释。
"""

REFLECT_PROMPT_TEMPLATE = """
你是一位极其严格的代码评审专家和资深算法专家，对代码的性能有着极致的要求。
你的任务是审查以下代码，并专注于找出其中在<strong>算法效率<\strong>上的主要瓶颈。

# 原始任务：{task}
# 待审查代码：
```Python
{code}
```

请分析该代码的时间复杂度，并思考是否存在一种<strong>算法上更优<\strong>的解决方案来显著提升性能。
如果存在，清晰地指出当前算法的不足，并提出具体的、可行的算法改进建议。
只有代码在算法层面上已经达到最优，才能回答“无需改进”。

请直接输出你的反馈，不需要任何解释。
"""

REFINE_PROMPT_TEMPLATE = """
你是一位资深的Python程序员。你正在根据一位代码评审专家的反馈来优化你的代码。

# 原始任务：{task}
# 你上一轮尝试的代码：{last_code_attemp}
# 评审员的反馈：{feedback}

根据评审员的反馈，生成一个优化后的新版本代码。
你的代码中必须包含完整函数签名、文档字符串，并遵循PEP 8编码规范。
直接输出优化后的代码，不要包含任何额外的解释。
"""

from llm_client import HelloAgentLLMClient
from reflection_demo.memory import Memory

class ReflectionAgent:
    def __init__(self, llm_client: HelloAgentLLMClient, max_iterations: int=3):
        self.llm_client = llm_client
        self.memory = Memory()
        self.max_iterations = max_iterations

    def run(self, task: str):
        print(f"Start process task: {task}")

        print(f"Initial attempt...")
        initial_prompt = INITITAL_PROMPT_TEMPLATE.format(task=task)
        initial_code = self._get_llm_response(initial_prompt)
        self.memory.add_record(record_type='execution', content=initial_code)

        for i in range(self.max_iterations):
            print(f"Processing {i+1}/{self.max_iterations}")

            print("Reflecting...")
            last_code = self.memory.get_last_execution()
            reflect_promot = REFLECT_PROMPT_TEMPLATE.format(task=task, code=last_code)
            feedback = self._get_llm_response(reflect_promot)
            self.memory.add_record(record_type="relection", content=feedback)

            if "无需改进" in feedback:
                print ("Finished")
                break

            print("Optimzing...")
            refine_prompt = REFINE_PROMPT_TEMPLATE.format(task=task, last_code_attemp=last_code, feedback=feedback)
            refine_code = self._get_llm_response(prompt=refine_prompt)
            self.memory.add_record(record_type='execution', content=refine_code)
        
        final_code = self.memory.get_last_execution()
        print(f"Finished refelction, result:\n ```Python\n{final_code}\n```")
        return final_code

    def _get_llm_response(self, prompt: str) -> str:
        message = [{"role": "user", "content": prompt}]
        response = self.llm_client.think(messages=message) or ""
        return response
    
if __name__ == '__main__':
    task = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"
    llm_client = HelloAgentLLMClient()
    reflection_agent = ReflectionAgent(llm_client=llm_client)
    final_code = reflection_agent.run(task=task)
    