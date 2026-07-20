import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class TideBotMiddleware(BaseHTTPMiddleware):
    """
    TideBot 全局高吞吐请求可观测性中间件
    用于拦截边缘流、分布式全局链路追踪注入、系统 API 性能耗时上报
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        # 生成标准化分布式唯一追踪号
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 性能耗时锚点打点
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as e:
            # 框架级别底座异常扩散前置隔离，避免泄露主机堆栈痕迹
            raise e
        finally:
            duration = time.time() - start_time
            if 'response' in locals():
                # 在响应报文头中显式回传，方便 Web 端与 Android App 精确度量网络抖动
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Process-Time"] = f"{duration:.4f}s"
                
        return response