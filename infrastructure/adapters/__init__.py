"""
TideBot IM 通道原生适配驱动器包
"""

from infrastructure.adapters.wechat import WeChatAdapter
from infrastructure.adapters.qq import QQAdapter
from infrastructure.adapters.telegram import TelegramAdapter

__all__ = ["WeChatAdapter", "QQAdapter", "TelegramAdapter"]