from typing import List, Dict, Any
from pydantic import BaseModel, Field

class AgentContext(BaseModel):
    """
    维护单次 Agent 执行生命周期内的上下文状态。
    可以在不同的执行步骤（规划、工具调用、总结）之间传递数据。
    """
    session_id: str
    user_id: str
    original_query: str
    # 存储当次交互的历史对话和正在生成的中间思考
    messages: List[Dict[str, str]] = Field(default_factory=list)
    # 用于存放执行过程中的临时数据，比如工具调用的返回值
    scratchpad: Dict[str, Any] = Field(default_factory=dict)
    
    # 执行状态标记
    is_finished: bool = False
    final_answer: str = ""