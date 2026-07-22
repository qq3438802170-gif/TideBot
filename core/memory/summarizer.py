import logging
from typing import List, Dict
from core.llm.router import LLMRouter

logger = logging.getLogger("TideBot")

class MemorySummarizer:
    """长期记忆提炼逻辑：当对话过长时，利用 LLM 将冷数据压缩为摘要"""
    
    def __init__(self):
        self.llm_router = LLMRouter()

    async def summarize(self, old_messages: List[Dict[str, str]]) -> str:
        """
        利用大模型将一段历史对话提取为精简的上下文摘要
        """
        if not old_messages:
            return ""
            
        chat_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in old_messages])
        prompt = (
            "请作为一名专业的助理，提取以下对话的核心信息和用户的关键偏好。\n"
            "忽略寒暄，只保留对后续对话有帮助的客观事实。\n\n"
            f"【历史对话记录】\n{chat_text}\n\n"
            "【摘要总结】："
        )
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self.llm_router.generate(messages=messages, temperature=0.3)
            summary = response.get("content", "").strip()
            logger.info("已成功生成历史对话摘要。")
            return summary
        except Exception as e:
            logger.error(f"生成记忆摘要失败: {e}", exc_info=True)
            # 如果总结失败，为了系统稳定，返回空或降级处理
            return "（历史记忆总结失败，部分上下文已丢弃）"