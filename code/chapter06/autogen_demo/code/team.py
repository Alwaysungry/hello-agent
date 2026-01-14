from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination

from model_client import create_deepseek_model_client

from agents.engineer import create_engineer_agent
from agents.product_manager import create_product_manager_client
from agents.code_reviewer import create_code_reviewer_agent
from agents.user_proxy import create_user_proxy_agent

def create_team_chat():
    """Create a team of agents for the software development workflow."""
    model_client = create_deepseek_model_client()

    product_manager = create_product_manager_client(model_client=model_client)
    engineer = create_engineer_agent(model_client=model_client)
    code_reviewer = create_code_reviewer_agent(model_client=model_client)
    user_proxy = create_user_proxy_agent(model_client=model_client)

    team_chat = RoundRobinGroupChat(
        participants = [
            product_manager,
            engineer,
            code_reviewer,
            user_proxy,
        ],
        termination_condition = TextMentionTermination("TERMINATE"),
        max_turns = 20,
    )
    return team_chat