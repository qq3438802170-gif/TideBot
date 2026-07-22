import subprocess
import threading
import logging
from core.config_manager import ConfigManager

logger = logging.getLogger("TideBot")

class CloudflareTunnelManager:
    """
    内网穿透与公网映射自动化脚本
    依赖本地安装了 cloudflared 工具
    """
    def __init__(self):
        self.process = None
        self.token = ConfigManager().env.cf_tunnel_token

    def start_tunnel(self):
        if not self.token:
            logger.info("未配置 CF_TUNNEL_TOKEN，跳过内网穿透环节。")
            return

        def run_cloudflared():
            logger.info("正在启动 Cloudflare Tunnel 内网穿透...")
            try:
                # 调用系统命令执行 cloudflared
                self.process = subprocess.Popen(
                    ["cloudflared", "tunnel", "--no-autoupdate", "run", "--token", self.token],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in self.process.stdout:
                    if "Registered tunnel connection" in line:
                        logger.info("✔ Cloudflare Tunnel 映射成功，公网可访问！")
            except FileNotFoundError:
                logger.error("未找到 cloudflared 命令，请先安装。跳过内网穿透。")
            except Exception as e:
                logger.error(f"Cloudflare Tunnel 运行异常: {e}")

        # 在后台线程运行，避免阻塞主服务的启动
        thread = threading.Thread(target=run_cloudflared, daemon=True)
        thread.start()

    def stop_tunnel(self):
        if self.process:
            self.process.terminate()
            logger.info("已终止 Cloudflare Tunnel。")