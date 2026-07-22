from fastapi import APIRouter, Depends, HTTPException
from schemas.chat import ChatRequest, ChatResponse
from core.security.auth import get_current_user
from core.agent.context import AgentContext
from core.agent.executor import AgentExecutor
import time
import logging

logger = logging.getLogger("TideBot")
router = APIRouter(prefix="/api/v1/app", tags=["App Client API"])

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    App 端发起的标准同步聊天接口
    """
    start_time = time.time()
    
    # 构造 Agent 运行时上下文
    context = AgentContext(
        session_id=request.session_id,
        user_id=current_user.get("user_id"),
        original_query=request.query,
        messages=[msg.model_dump() for msg in request.history] + [{"role": "user", "content": request.query}]
    )
    
    executor = AgentExecutor()
    try:
        # 触发 Agent 执行引擎
        final_answer = await executor.execute(context)
        
        processing_time = int((time.time() - start_time) * 1000)
        return ChatResponse(
            session_id=request.session_id,
            reply=final_answer,
            processing_time_ms=processing_time
        )
    except Exception as e:
        logger.error(f"聊天接口发生严重异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部推理错误")