"""
LLM Client
"""
import os

from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

def create_deepseek_model_client():
    return OpenAIChatCompletionClient(
        model = os.getenv("LLM_MODEL_ID", "deepseek-chat"),
        api_key = os.getenv("LLM_API_KEY"),
        base_url = os.getenv("LLM_BASE_URL"),
        model_info={ 
            "function_calling": True, 
            "max_tokens": 4096, 
            "context_length": 32768,
            "json_output": True,
            "structured_output": True, 
            "vision": False,
            "family": "deepseek"
        }
    )