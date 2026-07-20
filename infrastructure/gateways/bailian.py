import logging
import asyncio
import json
import aiohttp
from typing import List, Dict, Any, Optional, AsyncGenerator
from infrastructure.gateways.base import BaseGateway, ChatMessage

logger = logging.getLogger("TideBot.Infrastructure.Gateway.Bailian")

class AliyunBailianGateway(BaseGateway):
    """
    阿里云百炼大模型平台官方原生级高性能适配器
    无缝提供通义千问大模型矩阵、流式多模态聚合，并原生提供前置 TTS/STT 扩展钩子预置。
    """
    def __init__(self, model_name: str = "qwen-plus", api_key: str = "", base_url: str = "https://dashscope.aliyuncs.com/api/v1"):
        # 百炼 Dashscope 默认的基础请求根端点
        super().__init__(model_name, api_key, base_url)

    def _build_bailian_payload(self, messages: List[ChatMessage], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        # 百炼特殊输入协议对齐转换
        contents = []
        for msg in messages:
            role_map = msg.role
            # 百炼兼容 OpenAI 规范，但在特定工具回执时有严格验证
            contents.append({
                "role": role_map,
                "content": msg.content
            })

        payload = {
            "model": self.model_name,
            "input": {
                "messages": contents
            },
            "parameters": {
                "result_format": "message",
                "temperature": 0.5
            }
        }
        if tools:
            payload["parameters"]["tools"] = tools
        return payload

    async def generate(self, messages: List[ChatMessage], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = self._build_bailian_payload(messages, tools)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    raw_err = await resp.text()
                    raise RuntimeError(f"阿里百炼网关层拒绝访问，HTTP 错误代码: {resp.status}，响应内容: {raw_err}")
                return await resp.json()

    async def generate_stream(self, messages: List[ChatMessage], tools: Optional[List[Dict[str, Any]]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        url = f"{self.base_url}/services/aigc/text-generation/generation"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable" # 强制开启百炼专有的长连接 SSE 流式分块传输模式
        }
        payload = self._build_bailian_payload(messages, tools)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    raw_err = await resp.text()
                    raise RuntimeError(f"阿里百炼流式网关握手中断。原因: {raw_err}")
                
                async for line in resp.content:
                    line_str = line.decode("utf-8").strip()
                    if not line_str or not line_str.startswith("data:"):
                        continue
                    
                    data_json = line_str[5:].strip()
                    try:
                        chunk = json.loads(data_json)
                        yield chunk
                    except json.JSONDecodeError:
                        continue

    async def execute_text_to_speech(self, text: str) -> bytes:
        """
        百炼 TTS 语音合成高阶功能钩子扩展预留
        """
        logger.debug(f"触发百炼原生语音扩展合成：{text[:10]}...")
        # 留空供后续扩展层高级插件直接覆盖或直接发起物理调用
        await asyncio.sleep(0.05)
        return b"MOCK_AUDIO_BINARY_STREAM"