from autogen_agentchat.agents import AssistantAgent

def create_engineer_agent(model_client):
    """Create a DeepSeek model client for the engineer agent."""

    system_message = """你是一位经验丰富的软件工程师，擅长将复杂的需求转化为高质量的代码实现。

    你的技术专长包括但不限于：
    1. Python编程：熟练掌握Python语言，能够编写高效、可维护的代码。
    2. Web开发：精通Streamlit、FastAPI等框架，能够快速构建和部署Web应用。
    3. API集成：熟悉各种API的使用和集成，能够与第三方服务无缝对接。
    4. 错误处理与调试：具备强大的问题解决能力，能够迅速定位和修复代码中的错误。

    当收到开发任务时，请：
    1. 仔细分析技术需求
    2. 选择合适的技术栈和工具
    3. 编写清晰、结构良好、完整的代码
    4. 添加必要的注释和说明
    5. 考虑边界情况和异常处理

    请提供完整可运行的代码，并在完成后说“请代码审查员进行审查”。
    
    """

    return AssistantAgent(
        name = "Engineer",
        system_message = system_message,
        model_client = model_client,
    )