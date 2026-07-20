"""
多模态大模型基础设施中继网关
"""

from infrastructure.gateways.base import BaseGateway, ChatMessage, MultimodalContent
from infrastructure.gateways.openai import OpenAIGateway
from infrastructure.gateways.bailian import AliyunBailianGateway

__all__ = ["BaseGateway", "ChatMessage", "MultimodalContent", "OpenAIGateway", "AliyunBailianGateway"]