import logging
import json
import aiohttp
from typing import List, Dict, Any, Optional, AsyncGenerator
from infrastructure.gateways.base import BaseGateway, ChatMessage

logger = logging.getLogger("TideBot.Infrastructure.Gateway.OpenAI")

class OpenAIGateway(BaseGateway):
    """
    OpenAI / DeepSeek / 零一万物大模型标准协议流式高性能接入网关
    采用原生 aiohttp 极低损耗 SSE 文本行流事件流解析。
    """
    def __init__(self, model_name: str, api_key: str, base_url: str = "https://api.openai.com/v1"):
        super().__init__(model_name, api_key, base_url)

    def _prepare_payload(self, messages: List[ChatMessage], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        # 转换并解析核心层消息实体为 OpenAI 标准协议 Payload 矩阵
        formatted_messages = []
        for msg in messages:
            item = {"role": msg.role, "content": msg.content}
            if msg.name:
                item["name"] = msg.name
            if msg.tool_calls:
                item["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                item["tool_call_id"] = msg.tool_call_id
            formatted_messages.append(item)

        payload = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": 0.7
        }
        if tools:
            payload["tools"] = tools
        return payload

    async def generate(self, messages: List[ChatMessage], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = self._prepare_payload(messages, tools)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status != 200:
                        err_text = await resp.text()
                        raise RuntimeError(f"OpenAI 边缘节点网关返回阻断，状态码: {resp.status}, 详情: {err_text}")
                    return await resp.json()
            except Exception as e:
                logger.error(f"OpenAI 接口请求异常引发错误: {str(e)}")
                raise e

    async def generate_stream(self, messages: List[ChatMessage], tools: Optional[List[Dict[str, Any]]] = None) -> AsyncGenerator[Dict[str, Any], None]:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = self._prepare_payload(messages, tools)
        payload["stream"] = True

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    err_text = await resp.text()
                    raise RuntimeError(f"OpenAI SSE 流断开，状态码: {resp.status}, 原因: {err_text}")
                
                # SSE 行事件流解码器
                async for line in resp.content:
                    line_str = line.decode("utf-8").strip()
                    if not line_str or not line_str.startswith("data:"):
                        continue
                    
                    data_body = line_str[5:].strip()
                    if data_body == "[DONE]":
                        break
                        
                    try:
                        chunk = json.loads(data_body)
                        yield chunk
                    except json.JSONDecodeError:
                        continue