from core.llm.router import LLMRouter
import logging

logger = logging.getLogger("TideBot")

class TaskPlanner:
    """复杂任务意图拆解与规划器"""
    
    def __init__(self):
        self.llm_router = LLMRouter()
        
    async def analyze_intent(self, user_query: str) -> str:
        """
        前置分析：判断用户的输入是否属于复杂任务，是否需要多步规划
        （此处为基础实现，复杂生产环境可输出 JSON 结构化的步骤清单）
        """
        prompt = (
            f"分析以下用户的请求，简要说明需要完成这个请求的关键步骤或需要用到的工具类型。\n"
            f"用户请求：{user_query}"
        )
        
        try:
            response = await self.llm_router.generate(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return response.get("content", "无复杂意图，可直接回复。")
        except Exception as e:
            logger.error(f"意图分析失败: {e}", exc_info=True)
            return "直接对话"