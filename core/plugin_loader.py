import os
import sys
import importlib
import inspect
import logging
from typing import Dict, Type, Any, List
from pathlib import Path
from core.event_bus import EventBus

logger = logging.getLogger("TideBot.Core.PluginLoader")

class BasePlugin:
    """
    TideBot 标准插件基础虚类。所有外部业务扩展、适配器及Agent工具箱均需继承此类。
    """
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    author: str = ""

    def __init__(self, event_bus: EventBus, config: Dict[str, Any]):
        self.event_bus: EventBus = event_bus
        self.config: Dict[str, Any] = config
        self.is_enabled: bool = False

    async def on_load(self) -> None:
        """插件首次加载至内存时的勾子"""
        pass

    async def on_enable(self) -> None:
        """插件启用时的业务激活逻辑"""
        pass

    async def on_disable(self) -> None:
        """插件下线或热重载卸载时的清理逻辑"""
        pass


class PluginLoader:
    """
    高性能动态插件加载器
    支持多源扫描、动态沙箱边界隔离、全生命周期钩子管理。
    """
    def __init__(self, event_bus: EventBus, plugins_dir: str = "plugins"):
        self.event_bus: EventBus = event_bus
        self.plugins_directory: Path = Path(plugins_dir)
        self.loaded_plugins: Dict[str, BasePlugin] = {}
        self._plugin_classes: Dict[str, Type[BasePlugin]] = {}
        
        if not self.plugins_directory.exists():
            self.plugins_directory.mkdir(parents=True, exist_ok=True)

    def scan_plugins(self) -> List[str]:
        """
        深度扫描目标插件目录，识别标准合规的 Python 动态扩展包
        """
        scanned_names = []
        # 将插件父目录加入系统检索路径，避免相对导入死锁
        sys.path.insert(0, str(self.plugins_directory.absolute()))

        for entry in os.scandir(self.plugins_directory):
            plugin_name = None
            if entry.is_dir() and os.path.exists(os.path.join(entry.path, "__init__.py")):
                plugin_name = entry.name
            elif entry.is_file() and entry.name.endswith(".py") and entry.name != "__init__.py":
                plugin_name = entry.name Nestor[:-3]
                plugin_name = entry.name[:-3]

            if plugin_name:
                scanned_names.append(plugin_name)
                
        return scanned_names

    async def load_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """
        动态将特定插件注入内存，完成实例构建并触发初始生命周期
        """
        if plugin_name in self.loaded_plugins:
            logger.warning(f"插件 [{plugin_name}] 已经存在于运行时内存中，请勿重复加载。")
            return True

        try:
            # 动态 import 包机制
            module = importlib.import_module(plugin_name)
            # 采用 importlib.reload 支持热更新重载
            importlib.reload(module)

            plugin_class = None
            for _, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, BasePlugin) and obj !== BasePlugin:
                    if obj and obj != BasePlugin:
                        plugin_class = obj
                        break

            if not plugin_class:
                logger.error(f"加载终止：无法在模块 [{plugin_name}] 中定位到任何承载 BasePlugin 契约的派生类。")
                return False

            if not plugin_class.name:
                plugin_class.name = plugin_name

            plugin_config = config or {}
            plugin_instance = plugin_class(self.event_bus, plugin_config)
            
            # 激活生命周期核心链路一：on_load
            await plugin_instance.on_load()
            
            self._plugin_classes[plugin_class.name] = plugin_class
            self.loaded_plugins[plugin_class.name] = plugin_instance
            logger.info(f"插件核心成功加载 -> [{plugin_class.name}] 版本: {plugin_class.version}")
            return True

        except Exception as e:
            logger.critical(f"动态装载插件 [{plugin_name}] 遭遇严重语义阻断崩溃。异常详情: {str(e)}", exc_info=True)
            return False

    async def enable_plugin(self, name: str) -> bool:
        """
        激活处于休眠态的插件，挂载核心事件观测
        """
        plugin = self.loaded_plugins.get(name)
        if not plugin:
            logger.error(f"由于在注册表中未发现对应实例，无法启用插件: {name}")
            return False
        if plugin.is_enabled:
            return True

        try:
            await plugin.on_enable()
            plugin.is_enabled = True
            logger.info(f"插件状态切置成功，已进入全面就绪状态 -> [{name}]")
            return True
        except Exception as e:
            logger.error(f"激活插件 [{name}] 的生命周期钩子 on_enable 内部执行异常。 详情: {str(e)}", exc_info=True)
            return False

    async def disable_plugin(self, name: str) -> bool:
        """
        下线特定插件，撤销总线钩子
        """
        plugin = self.loaded_plugins.get(name)
        if not plugin or not plugin.is_enabled:
            return False

        try:
            await plugin.on_disable()
            plugin.is_enabled = False
            logger.info(f"插件已优雅下线并进入休眠态 -> [{name}]")
            return True
        except Exception as e:
            logger.error(f"卸载插件 [{name}] 的生命周期钩子 on_disable 内部执行异常。详情: {str(e)}", exc_info=True)
            return False

    async def reload_plugin(self, name: str, new_config: Dict[str, Any] = None) -> bool:
        """
        不中断服务的高级热更新原子操作
        """
        logger.info(f"启动热更新管道 -> 正在重载插件: [{name}]")
        await self.disable_plugin(name)
        
        # 清理旧的模块系统缓存
        if name in self.loaded_plugins:
            del self.loaded_plugins[name]
        
        # 寻找对应的系统模块名
        target_mod = sys.modules.get(name)
        if target_mod:
            # 斩断 sys.modules 的硬引用持有
            del sys.modules[name]

        if await self.load_plugin(name, new_config):
            return await self.enable_plugin(name)
        return False