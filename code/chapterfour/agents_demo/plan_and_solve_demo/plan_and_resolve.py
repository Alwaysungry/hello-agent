from llm_client import HelloAgentLLMClient
from plan_and_solve_demo.planner import Planner
from plan_and_solve_demo.executor import Executor
class PlanAndSolveAgent:
    def __init__(self, llm_client: HelloAgentLLMClient):
        self.llm_client = llm_client
        self.planner = Planner(llm_client)
        self.executor = Executor(llm_client)

    def run(self, question: str) -> str:
        print("\n=== Planning Phase ===")
        plan = self.planner.create_plan(question)
        if not plan:
            return "无法生成有效的计划。"

        print("\n生成的计划:")
        for i, step in enumerate(plan):
            print(f"步骤 {i + 1}: {step}")

        print("\n=== Execution Phase ===")
        history = []
        final_answer = self.executor.execute_step(question, plan, history, None)

        print("\n最终答案:")
        print(final_answer)
        return final_answer
    
if __name__ == "__main__":
    llm_client = HelloAgentLLMClient()
    agent = PlanAndSolveAgent(llm_client)

    user_question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果?"
    agent.run(user_question)