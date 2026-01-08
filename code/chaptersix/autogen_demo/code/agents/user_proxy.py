from autogen_agentchat.agents import UserProxyAgent

def create_user_proxy_agent(model_client):
    """Create a DeepSeek model client for the user proxy agent."""

    return UserProxyAgent(
        name = "UserProxy",
        description = """用户代理，负责以下职责：
        1. 代表用户提出开发需求
        2. 执行最终的代码实现
        3. 验证代码功能是否符合用户需求
        4. 提供用户反馈和建议
        完成测试后请回复 TERMINATE。
        """,
    )