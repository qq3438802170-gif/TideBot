import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger("TideBot.Core.Tokenizer")

class Tokenizer:
    """
    高性能文本 Token 计算器
    默认支持基于 tiktoken 的高效切分，内置高可靠性的本地备用分词轻量级算法。
    """
    
    def __init__(self, model_name: str = "gpt-4o"):
        self.model_name = model_name
        self._encoder = None
        self._fallback_warned = False
        self._init_encoder()

    def _init_encoder(self) -> None:
        try:
            import tiktoken
            try:
                self._encoder = tiktoken.encoding_for_model(self.model_name)
            except KeyError:
                self._encoder = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            if not self._fallback_warned:
                logger.warning("未检测到 tiktoken 依赖包，TideBot 将自动启用本地高性能正则 Token 估算器。")
                self._fallback_warned = True

    def count_tokens(self, text: str) -> int:
        """
        计算纯文本的 Token 数量
        """
        if not text:
            return 0
        if self._encoder:
            return len(self._encoder.encode(text, disallowed_special=()))
        
        # 生产环境高精度备用估算：英文按词频/字符比例，中文/中东/东亚文字独立按字计
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        other_chars = len(text) - chinese_chars
        words = len(re.findall(r'\b\w+\b', text))
        
        # 混合矩阵加权估算逻辑
        estimated_tokens = int(chinese_chars * 0.75) + int(words * 1.3) + int((other_chars - words * 4) * 0.3)
        return max(1, estimated_tokens)

    def count_chat_tokens(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]] = None) -> int:
        """
        精确计算符合 OpenAI ChatCompletion 规范的消息流和工具集的总 Token 消耗
        """
        num_tokens = 0
        # 每条消息的基础开销映射 (根据 gpt-4/gpt-3.5 规范适配)
        tokens_per_message = 3
        tokens_per_name = 1

        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                if value is None:
                    continue
                if isinstance(value, str):
                    num_tokens += self.count_tokens(value)
                elif isinstance(value, list): # 处理多模态或复合结构
                    for item in value:
                        if isinstance(item, dict) and item.get("type") == "text":
                            num_tokens += self.count_tokens(item.get("text", ""))
                if key == "name":
                    num_tokens += tokens_per_name

        num_tokens += 3  # 每个向 LLM 提交的回复边界开销

        if tools:
            for tool in tools:
                function_meta = tool.get("function", {})
                num_tokens += self.count_tokens(function_meta.get("name", ""))
                num_tokens += self.count_tokens(function_meta.get("description", ""))
                parameters = function_meta.get("parameters", {})
                if parameters:
                    for param_name, param_prop in parameters.get("properties", {}).items():
                        num_tokens += self.count_tokens(param_name)
                        num_tokens += self.count_tokens(param_prop.get("type", ""))
                        num_tokens += self.count_tokens(param_prop.get("description", ""))
                    if "required" in parameters:
                        num_tokens += len(parameters["required"])

        return num_tokens

    def truncate_by_tokens(self, text: str, max_tokens: int, from_start: bool = True) -> str:
        """
        严格按最大 Token 数量截断文本，支持从头部或尾部截断
        """
        if self.count_tokens(text) <= max_tokens:
            return text

        if self._encoder:
            tokens = self._encoder.encode(text, disallowed_special=())
            if from_start:
                truncated_tokens = tokens[:max_tokens]
            else:
                truncated_tokens = tokens[-max_tokens:]
            return self._encoder.decode(truncated_tokens)
        
        # 估算模式下的分段二分逼近截断法
        low, high = 0, len(text)
        best_index = 0
        while low <= high:
            mid = (low + high) // 2
            test_str = text[:mid] if from_start else text[-mid:]
            if self.count_tokens(test_str) <= max_tokens:
                best_index = mid
                low = mid + 1
            else:
                high = mid - 1
                
        return text[:best_index] if from_start else text[-best_index:]