import os
import importlib.util
import logging
from core.config_manager import ConfigManager

logger = logging.getLogger("TideBot")

class PluginLoader:
    """SDK 插件动态加载器，扫描特定目录并加载第三方工具"""
    
    @staticmethod
    def load_all_plugins():
        config = ConfigManager().config
        plugin_dir = config.get("plugins", {}).get("plugin_dir", "./plugins")
        
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir, exist_ok=True)
            logger.info(f"插件目录不存在，已自动创建: {plugin_dir}")
            return

        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                file_path = os.path.join(plugin_dir, filename)
                
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 约定插件必须有一个 setup() 方法来注册工具
                    if hasattr(module, "setup"):
                        module.setup()
                        logger.info(f"成功加载插件: {module_name}")
                    else:
                        logger.warning(f"插件 {module_name} 缺失 setup() 函数，跳过加载。")
                except Exception as e:
                    logger.error(f"加载插件 {module_name} 失败: {e}", exc_info=True)