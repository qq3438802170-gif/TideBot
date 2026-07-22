import logging
from typing import List, Dict, Any, AsyncGenerator
from openai import AsyncOpenAI
from core.llm.base_provider import BaseLLMProvider
from core.config_manager import ConfigManager

logger = logging.getLogger("TideBot")

class OpenAIProvider(BaseLLMProvider):
    """OpenAI 官方接口及兼容接口实现"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        config = ConfigManager()
        self.api_key = api_key or config.env.openai_api_key
        self.base_url = base_url or config.env.custom_llm_base_url
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        self.default_model = config.config.get("llm", {}).get("default_model", "gpt-4o-mini")

    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        model = kwargs.get("model", self.default_model)
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048)
            )
            return {
                "content": response.choices[0].message.content,
                "usage": response.usage.model_dump() if response.usage else {}
            }
        except Exception as e:
            logger.error(f"OpenAI 生成失败: {e}", exc_info=True)
            raise e

    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        model = kwargs.get("model", self.default_model)
        try:
            stream_response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                stream=True
            )
            async for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI 流式生成失败: {e}", exc_info=True)
            raise e