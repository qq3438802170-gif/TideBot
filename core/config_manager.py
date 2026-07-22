import os
import yaml
from typing import Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

class EnvSettings(BaseSettings):
    """
    敏感环境变量配置加载器
    负责从系统环境或 .env 文件中加载敏感数据
    """
    database_url: str
    app_secret_key: str
    jwt_expiration_days: int = 30
    
    # API Keys
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    claude_api_key: str | None = None
    deepseek_api_key: str | None = None
    custom_llm_base_url: str | None = None
    cf_tunnel_token: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

class ConfigManager:
    """
    全局配置管理器 (单例模式)
    统筹管理环境变量 (.env) 和业务配置 (config.yaml)
    """
    _instance = None
    _env_settings: EnvSettings = None
    _yaml_config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """执行实际的配置加载逻辑"""
        self._env_settings = EnvSettings()
        self._load_yaml_config()

    def _load_yaml_config(self, config_path: str = "config.yaml"):
        """加载非敏感的业务配置文件"""
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self._yaml_config = yaml.safe_load(f) or {}
        else:
            raise FileNotFoundError(f"未找到核心配置文件: {config_path}")

    @property
    def env(self) -> EnvSettings:
        """获取系统环境变量"""
        return self._env_settings

    @property
    def config(self) -> Dict[str, Any]:
        """获取业务配置参数"""
        return self._yaml_config

    def reload(self):
        """支持热加载配置，重新读取 config.yaml"""
        self._load_yaml_config()