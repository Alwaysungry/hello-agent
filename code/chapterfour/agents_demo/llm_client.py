import os

from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

class HelloAgentLLMClient:
    """
    LLM Client for interacting with the DeepSeek API.
    """
    def __init__(self, model: str = None, api_key: str = None, base_url: str = None, timeout: int = 60):
        self.model = model or os.getenv("LLM_MODEL_ID")
        api_key = api_key or os.getenv("LLM_API_KEY")
        base_url = base_url or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not all([self.model, api_key, base_url]):
            raise ValueError("Model, API key, and Base URL must be provided either as arguments or environment variables.")
        
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)

    def think(self, messages: List[Dict[str, Any]], max_tokens: int = 512, temperature: float = 0.7) -> str:
        """
        Send a chat completion request to the LLM API.

        :param messages: List of message dicts with 'role' and 'content'.
        :param max_tokens: Maximum number of tokens to generate.
        :param temperature: Sampling temperature.(0: deterministic, 0.2-0.5: conservative, 0.7-1.0: creative, >1.0: very creative)
        :return: The generated response from the model.
        """
        print (f"Calling model: {self.model} with messages: {messages}")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True, # Enable streaming responses
            )
            # Collect the streamed response
            print ("Receiving streamed response:")
            collected_content = []
            for chunk in response:
                content = chunk.choices[0].delta.content or ''
                print(content, end='', flush=True)  # Print each chunk as it arrives
                collected_content.append(content)
            print()  # New line after the complete response
            return ''.join(collected_content)
        except Exception as e:
            print(f"Error during LLM API call: {e}")
            return "Error: Unable to get response from LLM."