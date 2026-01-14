import asyncio

from team import create_team_chat

async def run_software_development_workflow():
    """Run the software development workflow using the agent team."""
    task = """我们需要开发一个比特币价格显示应用，具体要求如下：
            核心功能：
            - 实时显示比特币当前价格（USD）
            - 显示24小时价格变化趋势（涨跌幅和涨跌额）
            - 提供价格刷新功能

            技术要求：
            - 使用 Streamlit 框架创建 Web 应用
            - 界面简洁美观，用户友好
            - 添加适当的错误处理和加载状态

            请团队协作完成这个任务，从需求分析到最终实现。
"""
    team_chat = create_team_chat()
    async for event in team_chat.run_stream(task=task): print(event)

if __name__ == "__main__":
    asyncio.run(run_software_development_workflow())