import logging
from typing import List, Dict, Any, AsyncGenerator
from core.config_manager import ConfigManager
from core.llm.base_provider import BaseLLMProvider
from core.llm.provider_openai import OpenAIProvider

logger = logging.getLogger("TideBot")

class LLMRouter:
    """
    系统 LLM 路由调度中心。
    负责根据配置初始化提供商，并提供容灾和统一调用入口。
    """
    def __init__(self):
        self.config = ConfigManager()
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider_name = self.config.config.get("llm", {}).get("default_provider", "openai")
        self._initialize_providers()

    def _initialize_providers(self):
        """初始化所有支持的模型驱动"""
        env = self.config.env
        if env.openai_api_key or env.custom_llm_base_url:
            self.providers["openai"] = OpenAIProvider(api_key=env.openai_api_key, base_url=env.custom_llm_base_url)
        # TODO: 可以在这里添加 provider_gemini 等其它模型的初始化逻辑

    def get_provider(self, provider_name: str = None) -> BaseLLMProvider:
        """获取指定的模型提供商，默认走配置文件的设定"""
        target = provider_name or self.default_provider_name
        if target not in self.providers:
            logger.warning(f"提供商 {target} 未初始化，尝试回退到默认 openai 提供商。")
            if "openai" in self.providers:
                return self.providers["openai"]
            raise ValueError(f"没有可用的 LLM 提供商来处理请求！")
        return self.providers[target]

    async def generate(self, messages: List[Dict[str, str]], provider_name: str = None, **kwargs) -> Dict[str, Any]:
        """统一生成入口"""
        provider = self.get_provider(provider_name)
        return await provider.generate(messages, **kwargs)

    async def stream(self, messages: List[Dict[str, str]], provider_name: str = None, **kwargs) -> AsyncGenerator[str, None]:
        """统一流式生成入口"""
        provider = self.get_provider(provider_name)
        async for chunk in provider.stream(messages, **kwargs):
            yield chunk