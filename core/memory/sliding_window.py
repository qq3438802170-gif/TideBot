from typing import List, Dict

class SlidingWindowMemory:
    """基于消息轮数的滑动窗口记忆管理"""
    
    def __init__(self, max_window_size: int = 15):
        self.max_window_size = max_window_size

    def truncate(self, system_prompt: Dict[str, str], history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        截断历史记录，保证总是不超过最大窗口限制。
        强制保留 system_prompt。
        """
        if len(history) <= self.max_window_size:
            return [system_prompt] + history
            
        # 截取最近的 max_window_size 条记录
        truncated_history = history[-self.max_window_size:]
        
        # 组装返回，系统提示词永远在最前
        return [system_prompt] + truncated_history