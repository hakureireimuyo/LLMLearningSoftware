
"""
这里管理所有LLMProviderBase的子类
通过传入指定数据初始化实例以及参数
提供深层拷贝的实例对象给combo类使用
"""
import copy
from typing import Dict, Type, Any, List, Optional, Union
from .provider import LLMProviderBase
from .zhipu import ZhipuAIProvider

class ProviderGroup:
    """
    管理多个LLM提供者配置的"弹夹"类
    负责从数据库加载配置并创建深拷贝实例
    """
    
    def __init__(self):
        # 存储提供者类而不是实例
        self._provider_classes: Dict[str, Type[LLMProviderBase]] = {}
        # 存储配置数据
        self._provider_configs: Dict[str, Dict[str, Any]] = {}
        # 注册提供者类
        self.register_provider("zhipu", ZhipuAIProvider)

    def register_provider(self, provider_name: str, provider_class: Type[LLMProviderBase]):
        """注册提供者类"""
        self._provider_classes[provider_name] = provider_class
        self._provider_configs[provider_name] = {
            "voucher": {},
            "params": {}
        }
    
    def load_from_data(self, providers_data: List[Dict[str, Any]]) -> None:
        """
        从数据库加载所有提供者配置
        配置信息存储在内部字典中
        """
        for config in providers_data:
            provider_type = config["type"]
            if provider_type not in self._provider_classes:
                continue
                
            # 存储凭证和参数配置
            self._provider_configs[provider_type]["voucher"] = config["voucher"]
            self._provider_configs[provider_type]["params"] = config["params"]
    
    def update_provider_config(self, provider_type: str, updates: Dict[str, Any]):
        """更新特定提供者的配置"""
        if provider_type not in self._provider_configs:
            raise KeyError(f"提供者ID不存在: {provider_type}")
        
        # 合并更新配置
        self._provider_configs[provider_type]["params"].update(updates)
    
    def create_provider(self, provider_type: str) -> LLMProviderBase:
        """
        创建提供者的新实例
        不使用深拷贝，而是直接创建新对象
        
        Returns:
            新创建的提供者实例，已根据配置初始化
        """
        if provider_type not in self._provider_classes:
            raise KeyError(f"提供者类型不存在: {provider_type}")
        
        # 获取提供者类和配置
        provider_class = self._provider_classes[provider_type]
        config = self._provider_configs[provider_type]
        
        # 创建新实例
        provider = provider_class()
        
        # 使用存储的凭证和参数初始化
        if config["voucher"]:
            provider.initialize(**config["voucher"])
        if config["params"]:
            provider.update_parameters(**config["params"])
        
        return provider
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """获取所有可用提供者摘要信息"""
        return [{
            "type": name,
            "provider": cls.__name__,
        } for name, cls in self._provider_classes.items()]