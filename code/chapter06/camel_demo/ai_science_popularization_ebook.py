from colorama import Fore
from camel.societies import RolePlaying
from camel.utils import print_text_animated
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from dotenv import load_dotenv
import os

load_dotenv()
LLM_API_KEY = os.environ.get("LLM_API_KEY")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL")
LLM_MODEL = os.environ.get("LLM_MODEL")

model = ModelFactory.create(
    model_platform=ModelPlatformType.DEEPSEEK,
    model_name=LLM_MODEL,
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
)

task_prompt = """
创作一本关于人工智能科普的电子书，目标读者是对人工智能感兴趣但缺乏专业知识的普通大众。电子书应涵盖以下几个方面：
1. 人工智能的基本概念和历史背景
2. 人工智能的主要技术和应用领域
3. 人工智能的发展趋势和未来展望
4. 人工智能对社会、经济和伦理的影响
5. 篇幅控制在5000字左右
6. 结构清晰，语言通俗易懂，包含核心章节和总结。
"""

print(Fore.GREEN + f"任务描述: {task_prompt}" + Fore.RESET)

role_play_session = RolePlaying(
    assistant_role_name = "人工智能领域科学家",
    user_role_name = "科普电子书作者",
    task_prompt = task_prompt,
    model = model,
    with_task_specify=False,
)

print (Fore.CYAN + f"具体任务描述:\n{role_play_session.task_specify_prompt}\n" + Fore.RESET)

chat_turn_limit, n = 15, 0
input_message = role_play_session.init_chat()

while n < chat_turn_limit:
    n += 1
    print(Fore.MAGENTA + f"第 {n} 轮对话:" + Fore.RESET)

    assistant_response, user_response = role_play_session.step(input_message)

    if assistant_response.msg is None or user_response.msg is None:
        print(Fore.RED + "对话过程中出现错误，结束对话。" + Fore.RESET)
        break

    print_text_animated(Fore.BLUE + f"{role_play_session.assistant_role_name}:\n{assistant_response.msg}\n" + Fore.RESET)
    print_text_animated(Fore.GREEN + f"{role_play_session.user_role_name}:\n{user_response.msg}\n" + Fore.RESET)

    if "<CAMEL_TASK_DONE>" in user_response.msg or "<CAMEL_TASK_DONE>" in assistant_response.msg:
        print(Fore.YELLOW + "任务完成标志已检测到，结束对话。" + Fore.RESET)
        break

    input_message = assistant_response.msg

print(Fore.YELLOW + f"对话结束，共进行了 {n} 轮对话。" + Fore.RESET)