from autogen_agentchat.agents import AssistantAgent

def create_code_reviewer_agent(model_client):
    """Create a DeepSeek model client for the code reviewer agent."""

    system_message = """你是一位经验丰富的代码审查员，专注于提升代码质量和维护性。

    你的核心职责包括：
    1. 代码质量检查：确保代码符合最佳实践和编码规范。
    2. 可读性评估：评估代码的可读性和结构，提出改进建议。
    3. 性能优化：识别潜在的性能瓶颈并提供优化建议。
    4. 安全审查：检查代码中的安全漏洞和风险。

    审查流程：
    1. 仔细阅读和理解代码逻辑
    2. 检查代码规范和最佳实践
    3. 识别潜在问题和改进点
    4. 提供具体的改进建议
    5. 评估代码的整体质量

    请提供具体的审查意见，并在审查完成后说“代码审查完成，请用户代理测试”。
    
    """

    return AssistantAgent(
        name = "CodeReviewer",
        system_message = system_message,
        model_client = model_client,
    )