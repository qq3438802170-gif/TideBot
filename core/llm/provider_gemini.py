import logging
from typing import List, Dict, Any, AsyncGenerator
import google.generativeai as genai
from core.llm.base_provider import BaseLLMProvider
from core.config_manager import ConfigManager

logger = logging.getLogger("TideBot")

class GeminiProvider(BaseLLMProvider):
    """Google Gemini 官方 API 实现"""
    
    def __init__(self, api_key: str = None):
        config = ConfigManager()
        self.api_key = api_key or config.env.gemini_api_key
        if not self.api_key:
            raise ValueError("未配置 Gemini API Key")
            
        genai.configure(api_key=self.api_key)
        self.default_model = config.config.get("llm", {}).get("default_model", "gemini-1.5-flash")

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """将 OpenAI 格式的 messages 转换为 Gemini 的格式"""
        gemini_msgs = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            # 如果有 system prompt，通常在初始化 Gemini 模型时作为 instruction 传入
            # 这里简化处理，将 system 作为第一个 user 消息发送
            if msg["role"] == "system":
                role = "user"
            gemini_msgs.append({"role": role, "parts": [msg["content"]]})
        return gemini_msgs

    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        model_name = kwargs.get("model", self.default_model)
        model = genai.GenerativeModel(model_name)
        formatted_messages = self._convert_messages(messages)
        
        try:
            # Gemini Python SDK 提供了 async 生成接口 (generate_content_async)
            response = await model.generate_content_async(
                formatted_messages,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get("temperature", 0.7),
                )
            )
            return {
                "content": response.text,
                "usage": {} # Gemini 暂未在标准返回值中提供严格对齐的 Token 统计
            }
        except Exception as e:
            logger.error(f"Gemini 生成失败: {e}", exc_info=True)
            raise e

    async def stream(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        model_name = kwargs.get("model", self.default_model)
        model = genai.GenerativeModel(model_name)
        formatted_messages = self._convert_messages(messages)
        
        try:
            response = await model.generate_content_async(
                formatted_messages,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=kwargs.get("temperature", 0.7),
                )
            )
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini 流式生成失败: {e}", exc_info=True)
            raise e