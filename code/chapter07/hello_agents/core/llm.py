import os

from openai import OpenAI
from typing import List, Dict, Any, Literal, Optional, Iterator

from core.exceptions import HelloAgentsException

SUPPORTED_PROVIDERS = Literal[
        "openai",
        "deepseek",
        "qwen",
        "modelscope",
        "kimi",
        "zhipu",
        "vllm",
        "ollama",
        "local",
        "custom",
        "auto",
]

class HelloAgentsLLMClient:
    """
    hello_agents的LLM客户端封装，支持与OpenAI兼容的API交互。
    1. 多提供商支持：实现对 OpenAI、ModelScope、智谱 AI 等多种主流 LLM 服务商的无缝切换，避免框架与特定供应商绑定。
    2. 本地模型集成：引入 VLLM 和 Ollama 这两种高性能本地部署方案，满足对数据隐私和低延迟的需求。
    3. 自动检测机制：通过智能检测用户环境，自动选择最合适的 LLM 方案，简化配置过程，提高用户体验。
    """
    def __init__(
        self, 
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        provider: Optional[SUPPORTED_PROVIDERS] = None,
        temprature: Optional[float] = 0.7,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = 60,
        **kwargs            
    ):
        """
        初始化客户端。优先使用传入的参数，其次使用环境变量。
        Args:
            model (str): 模型ID或名称。
            api_key (str): API密钥。
            base_url (str): API基础URL。
            provider (str): LLM服务提供商。
            temprature (float): 采样温度。
            max_tokens (int): 最大生成令牌数。
            timeout (int): 请求超时时间（秒）。
        """
        
        self.model = model or os.getenv("LLM_MODEL_ID")
        self.temperature = temprature or float(os.getenv("LLM_TEMPERATURE", 0.7))
        self.max_tokens = max_tokens or (int(os.getenv("LLM_MAX_TOKENS")) if os.getenv("LLM_MAX_TOKENS") else None)
        self.kwargs = kwargs
        self.timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        requested_provider = (provider or "").lower() if provider else None
        self.provider = provider or self._auto_detect_provider(api_key, base_url)

        if requested_provider == "custom":
            self.provider = "custom"
            self.api_key = api_key or os.getenv("LLM_API_KEY")
            self.base_url = base_url or os.getenv("LLM_API_BASE_URL")
        else:
            self.api_key, self.base_url = self._resolve_api_credentials(api_key, base_url)

        if not self.model:
            self.model = self._get_default_model()
        if not all([self.api_key, self.base_url]):
            raise HelloAgentsException("API key and base URL must be provided either as parameters or environment variables.")
    
        self._client = self._create_client()

    def _auto_detect_provider(self, api_key: Optional[str], base_url: Optional[str]) -> SUPPORTED_PROVIDERS:
        """
        自动检测LLM提供商。

        检测逻辑：
        1. 优先检查特定提供商的环境变量（如 DEEPSEEK_API_KEY）。
        2. 根据API密钥的格式判断
        3. 根据base_url判断
        4. 默认返回通用配置
        """
        provider_env_map = [
            ("modelscope", "MODELSCOPE_API_KEY"),
            ("openai", "OPENAI_API_KEY"),
            ("zhipu", "ZHIPU_API_KEY"),
            ("deepseek", "DEEPSEEK_API_KEY"),
            ("qwen", "QWEN_API_KEY"),
            ("kimi", "KIMI_API_KEY"),
        ]

        for provider_name, env_var in provider_env_map:
            if os.getenv(env_var):
                return provider_name  # 明确指定服务商的环境变量优先级最高

        candidate_base_url = (
            base_url
            or os.getenv("LLM_BASE_URL")
            or os.getenv("LLM_API_BASE_URL")
            or ""
        ).lower()

        if candidate_base_url:
            url_markers = {
                "modelscope": ["api-inference.modelscope.cn", "modelscope.cn"],
                "openai": ["api.openai.com"],
                "zhipu": ["open.bigmodel.cn", "bigmodel.cn", "zhipu"],
                "deepseek": ["api.deepseek.com"],
                "qwen": ["dashscope.aliyuncs.com", "dashscope.com", "qwen", "qianwen"],
                "kimi": ["moonshot.cn", "kimiapi.cn", "kimi.moonshot.cn"],
                "ollama": [":11434", "ollama"],
                "vllm": [":8000", "vllm"],
            }

            for provider_name, markers in url_markers.items():
                if any(marker in candidate_base_url for marker in markers):
                    return provider_name

            if candidate_base_url.startswith("http://localhost") or candidate_base_url.startswith("http://127.0.0.1"):
                return "local"

        candidate_key = api_key or os.getenv("LLM_API_KEY") or ""

        if candidate_key.startswith("ZHIPUAI_"):
            return "zhipu"
        if candidate_key.startswith("sk-"):
            # sk- 前缀兼容多家厂商，默认按 OpenAI 兼容接口处理
            return "openai"

        return "auto"

    def _resolve_api_credentials(self, api_key: Optional[str], base_url: Optional[str]) -> (str, str):
        """
        根据提供商解析API凭据。
        """
        provider = (self.provider or "auto")

        config = {
            "openai": {
                "key_env": ["OPENAI_API_KEY", "LLM_API_KEY"],
                "base_env": ["OPENAI_BASE_URL", "LLM_BASE_URL", "LLM_API_BASE_URL"],
                "default_base": "https://api.openai.com/v1",
            },
            "deepseek": {
                "key_env": ["DEEPSEEK_API_KEY", "LLM_API_KEY"],
                "base_env": ["DEEPSEEK_BASE_URL", "LLM_BASE_URL", "LLM_API_BASE_URL"],
                "default_base": "https://api.deepseek.com",
            },
            "qwen": {
                "key_env": ["QWEN_API_KEY", "DASHSCOPE_API_KEY", "LLM_API_KEY"],
                "base_env": ["QWEN_BASE_URL", "DASHSCOPE_BASE_URL", "LLM_BASE_URL", "LLM_API_BASE_URL"],
                "default_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            },
            "modelscope": {
                "key_env": ["MODELSCOPE_API_KEY", "LLM_API_KEY"],
                "base_env": ["MODELSCOPE_BASE_URL", "LLM_BASE_URL", "LLM_API_BASE_URL"],
                "default_base": "https://api-inference.modelscope.cn/v1",
            },
            "zhipu": {
                "key_env": ["ZHIPU_API_KEY", "LLM_API_KEY"],
                "base_env": ["ZHIPU_BASE_URL", "LLM_BASE_URL", "LLM_API_BASE_URL"],
                "default_base": "https://open.bigmodel.cn/api/paas/v4",
            },
            "kimi": {
                "key_env": ["KIMI_API_KEY", "LLM_API_KEY"],
                "base_env": ["KIMI_BASE_URL", "LLM_BASE_URL", "LLM_API_BASE_URL"],
                "default_base": "https://api.moonshot.cn/v1",
            },
            "ollama": {
                "key_env": ["OLLAMA_API_KEY", "LLM_API_KEY"],
                "base_env": ["OLLAMA_BASE_URL", "LLM_BASE_URL", "LLM_API_BASE_URL"],
                "default_base": "http://localhost:11434",
            },
            "vllm": {
                "key_env": ["VLLM_API_KEY", "LLM_API_KEY"],
                "base_env": ["VLLM_BASE_URL", "LLM_BASE_URL", "LLM_API_BASE_URL"],
                "default_base": "http://localhost:8000",
            },
            "local": {
                "key_env": ["LLM_API_KEY"],
                "base_env": ["LLM_BASE_URL", "LLM_API_BASE_URL"],
                "default_base": "http://localhost:8000",
            },
            "auto": {
                "key_env": ["LLM_API_KEY"],
                "base_env": ["LLM_BASE_URL", "LLM_API_BASE_URL"],
                "default_base": None,
            },
        }

        cfg = config.get(provider, config["auto"])

        def _first_non_empty(values):
            for val in values:
                if val:
                    return val
            return None

        resolved_key = _first_non_empty([api_key] + [os.getenv(env) for env in cfg["key_env"]])
        resolved_base = _first_non_empty([base_url] + [os.getenv(env) for env in cfg["base_env"]])

        if not resolved_base:
            resolved_base = cfg["default_base"]

        return resolved_key, resolved_base

    def _get_default_model(self) -> str:
        """
        获取默认模型ID。
        """
        provider_defaults = {
            "openai": "gpt-4o-mini",
            "deepseek": "deepseek-chat",
            "qwen": "qwen-turbo",
            "modelscope": "qwen-turbo",
            "zhipu": "glm-4-flash",
            "kimi": "moonshot-v1-8k",
            "ollama": "llama3",
            "vllm": "local-model",
            "local": "local-model",
            "custom": "custom-model",
            "auto": "gpt-4o-mini",
        }

        return provider_defaults.get(self.provider or "auto", "gpt-4o-mini")

    def _create_client(self) -> OpenAI:
        """
        创建OpenAI客户端实例。
        """
        return OpenAI(
            api_key=self.api_key,
            api_base=self.base_url,
            timeout=self.timeout,
        )

    def think(self, messages: List[Dict[str, Any]], temperature: Optional[float] = 0.7) -> Iterator[str]:
        """
        调用大语言模型进行推理，返回流式响应。
        主要的调用方法，默认使用流式响应
        Args:
            messages (List[Dict[str, Any]]): 消息列表，符合OpenAI聊天模型的输入格式。
            temperature (float): 采样温度。
        Returns:
            Iterator[str]: 流式响应生成器，每次迭代返回一部分内容
        """
        print (f"正在调用模型 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=temperature if temperature is not None else self.temperature,
                stream=True, # Enable streaming responses
            )
            # Collect the streamed response
            print ("大模型响应成功:")
            for chunk in response:
                content = chunk.choices[0].delta.get("content", "")
                if content:
                    print(content, end='', flush=True)
                    yield content
            print()  # For newline after completion
        except Exception as e:
            print(f"调用大语言模型API时出错: {e}")
            raise HelloAgentsException(f"LLM API调用失败: {e}")
        
    def invoke(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """
        非流式调用大语言模型，返回完整响应。
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                **{k: v for k, v in self.kwargs.items() if k not in ['temperature', 'max_tokens']},
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"调用大语言模型API时出错: {e}")
            raise HelloAgentsException(f"LLM API调用失败: {e}")
        
    def stream_invoke(self, messages: List[Dict[str, Any]], **kwargs) -> Iterator[str]:
        """
        流式调用大语言模型，与think方法相同。
        """
        temprature = kwargs.get("temperature", self.temperature)
        return self.think(messages, temperature=temprature)