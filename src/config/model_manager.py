#!/usr/bin/env python3
"""
模型配置管理器 - 负责读取和管理模型配置
"""

import os
import yaml
from pathlib import Path

class ModelManager:
    """模型配置管理器"""
    
    def __init__(self):
        # 获取项目根目录
        self.root_dir = Path(__file__).parent.parent.parent.absolute()
        self.config_path = os.path.join(self.root_dir, "config", "models.yaml")
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            "command": {
                "provider": "siliconflow",
                "models": {
                    "siliconflow": {
                        "url": "https://api.siliconflow.cn/v1/chat/completions",
                        "model": "Pro/deepseek-ai/DeepSeek-V3",
                        "token_limit": 128000,
                        "key_file": "config/api/siliconflow_key.txt"
                    }
                }
            },
            "script": {
                "provider": "openrouter",
                "models": {
                    "openrouter": {
                        "url": "https://openrouter.ai/api/v1/chat/completions",
                        "model": "anthropic/claude-3.7-sonnet",
                        "token_limit": 180000,
                        "key_file": "config/api/openrouter_key.txt"
                    }
                }
            }
        }
    
    def get_command_provider(self):
        """获取命令提供商配置"""
        provider_name = self.config["command"]["provider"]
        return self.config["command"]["models"][provider_name]
    
    def get_script_provider(self):
        """获取脚本提供商配置"""
        provider_name = self.config["script"]["provider"]
        return self.config["script"]["models"][provider_name]
    
    def get_api_key(self, key_file):
        """从文件读取API密钥"""
        full_path = os.path.join(self.root_dir, key_file)
        if os.path.exists(full_path):
            with open(full_path, "r") as f:
                return f.read().strip()
        return None
    
    def save_config(self):
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
    
    def set_provider(self, type_name, provider_name):
        """设置提供商"""
        if type_name not in ["command", "script"]:
            raise ValueError(f"未知的类型: {type_name}")
            
        if provider_name not in self.config[type_name]["models"]:
            raise ValueError(f"未知的提供商: {provider_name}")
            
        self.config[type_name]["provider"] = provider_name
        self.save_config()
    
    def add_provider(self, type_name, provider_name, url, model, token_limit, key_file):
        """添加新提供商"""
        if type_name not in ["command", "script", "both"]:
            raise ValueError(f"未知的类型: {type_name}")
        
        provider_config = {
            "url": url,
            "model": model,
            "token_limit": token_limit,
            "key_file": key_file
        }
        
        if type_name in ["command", "both"]:
            self.config["command"]["models"][provider_name] = provider_config
            
        if type_name in ["script", "both"]:
            self.config["script"]["models"][provider_name] = provider_config
            
        self.save_config()
    
    def get_model_token_limits(self):
        """获取所有模型的token限制"""
        limits = {}
        
        # 添加命令模型
        for provider, config in self.config["command"]["models"].items():
            limits[config["model"]] = config["token_limit"]
            
        # 添加脚本模型
        for provider, config in self.config["script"]["models"].items():
            limits[config["model"]] = config["token_limit"]
            
        return limits
