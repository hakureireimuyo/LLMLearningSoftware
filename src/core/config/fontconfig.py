import yaml
import logging
from pathlib import Path
from typing import Dict, Any

# 设置模块级别的日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 将处理器添加到记录器
logger.addHandler(console_handler)

DEFAULT_CONFIG = {
    "font_styles": {
        "default": {
            "large": {"size": 30, "line_height": 1.64},
            "medium": {"size": 20, "line_height": 1.52},
            "small": {"size": 16, "line_height": 1.0}
        }
    }
}

from src.core.evn import external_resource_path

class FontConfigManager:
    """字体配置管理类"""
    
    def __init__(self, config_path: str = external_resource_path("config/fontconfig.yaml")):
        self.config_path = Path(config_path)
        logger.info(f"初始化FontConfigManager，配置文件路径: {self.config_path}")
        self.config = self._load_or_create_config()
    
    def _load_or_create_config(self) -> Dict[str, Any]:
        """加载或创建配置文件"""
        if not self.config_path.exists():
            logger.warning(f"配置文件 {self.config_path} 不存在，将创建默认配置")
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                logger.debug(f"从 {self.config_path} 加载配置文件")
                return yaml.safe_load(f) or DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}, 将使用默认配置")
            return DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: dict) -> None:
        """保存配置文件"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
            logger.info(f"配置文件已保存到 {self.config_path}")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            raise
    
    def get_font_style(self, font_name: str) -> dict:
        """获取字体样式配置"""
        logger.debug(f"获取字体样式: {font_name}")
        return self.config["font_styles"].get(
            font_name,
            self.config["font_styles"]["default"]
        )
    
    def update_font_style(self, font_name: str, styles: dict) -> None:
        """更新字体配置"""
        logger.info(f"更新字体 {font_name} 的样式配置")
        self.config["font_styles"][font_name] = styles
        self._save_config(self.config)