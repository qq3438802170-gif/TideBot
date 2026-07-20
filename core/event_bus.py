import asyncio
import logging
from typing import Dict, List, Callable, Any, Awaitable, Union
from enum import IntEnum

logger = logging.getLogger("TideBot.Core.EventBus")

class EventPriority(IntEnum):
    """
    事件监听器执行优先级
    HIGHEST: 拦截器、安全审计、全面日志
    HIGH: 消息预处理、过滤、权限校验
    NORMAL: 标准业务处理逻辑、常规插件
    LOW: 后置状态统计、异步回执处理
    LOWEST: 非阻塞持久化、数据上报分析
    """
    HIGHEST = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    LOWEST = 4


class Event:
    """
    TideBot 全局统一事件上下文对象
    """
    def __init__(self, name: str, data: Dict[str, Any] = None):
        self.name: str = name
        self.data: Dict[str, Any] = data if data is not None else {}
        self.is_cancelled: bool = False
        self.result: Any = None
        self.exception: Exception = None

    def stop_propagation(self) -> None:
        """
        立即中断该事件在后续优先级总线上的向后传递
        """
        self.is_cancelled = True

    def set_result(self, res: Any) -> None:
        """
        设置事件的处理产出结果
        """
        self.result = res


class EventBus:
    """
    高性能、异步、分级阻断式系统事件总线
    """
    def __init__(self):
        # 核心字典树/哈希映射：event_name -> priority -> list[callbacks]
        self._listeners: Dict[str, Dict[EventPriority, List[Callable[[Event], Awaitable[None]]]]] = {}

    def subscribe(self, event_name: str, callback: Callable[[Event], Awaitable[None]], priority: EventPriority = EventPriority.NORMAL) -> None:
        """
        注册异步事件监听器
        """
        if not asyncio.iscoroutinefunction(callback):
            raise TypeError(f"事件监听器回调函数必须为异步协程方法(async def): {callback.__name__}")

        if event_name not in self._listeners:
            self._listeners[event_name] = {p: [] for p in EventPriority}

        if callback not in self._listeners[event_name][priority]:
            self._listeners[event_name][priority].append(callback)
            logger.debug(f"已成功向事件 [{event_name}] 注册优先级为 {priority.name} 的监听器: {callback.__name__}")

    def unsubscribe(self, event_name: str, callback: Callable[[Event], Awaitable[None]], priority: EventPriority = EventPriority.NORMAL) -> bool:
        """
        注销指定的事件监听器
        """
        if event_name in self._listeners and callback in self._listeners[event_name][priority]:
            self._listeners[event_name][priority].remove(callback)
            logger.debug(f"已注销事件 [{event_name}] 下优先级为 {priority.name} 的监听器: {callback.__name__}")
            return True
        return False

    async def publish(self, event: Event) -> Event:
        """
        发布事件，按照优先级严格由高到低串行执行。支持中途动态阻断（stop_propagation）。
        """
        if event.name not in self._listeners:
            return event

        priority_groups = self._listeners[event.name]
        
        for priority in EventPriority:
            listeners = priority_groups.get(priority, [])
            if not listeners:
                continue

            # 同一优先级内部采用并行调度，兼顾隔离性，防止单点崩溃波及全局总线
            tasks = []
            for listener in listeners:
                tasks.append(self._execute_listener(listener, event))
            
            if tasks:
                await asyncio.gather(*tasks)

            # 跨优先级检查阻断标记
            if event.is_cancelled:
                logger.debug(f"事件 [{event.name}] 已在 {priority.name} 阶段被监听器拦截并终止向后传递。")
                break

        return event

    async def _execute_listener(self, listener: Callable[[Event], Awaitable[None]], event: Event) -> None:
        """
        独立包裹执行单个监听器，防止异常导致整个异步链式调用崩溃
        """
        try:
            await listener(event)
        except Exception as e:
            logger.error(f"事件驱动链异常：监听器 [{listener.__name__}] 在处理事件 [{event.name}] 时崩溃。详情: {str(e)}", exc_info=True)
            event.exception = e
            # 严重安全隐私级崩溃或协议破坏时，默认激活熔断保护
            if priority := getattr(listener, "__critical_interceptor__", False):
                event.stop_propagation()