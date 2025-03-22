#!/usr/bin/env python3
"""
模型管理器测试用例
"""

import unittest
import os
import sys
import yaml
from unittest.mock import patch, mock_open

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.model_manager import ModelManager


class TestModelManager(unittest.TestCase):
    """模型管理器测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 模拟配置数据
        self.test_config = {
            "providers": {
                "openai": {
                    "name": "OpenAI",
                    "url": "https://api.openai.com/v1/chat/completions",
                    "models": ["gpt-3.5-turbo", "gpt-4"],
                    "key_file": "config/api/openai_key.txt"
                },
                "siliconflow": {
                    "name": "硅基流动",
                    "url": "https://api.siliconflow.com/v1/chat/completions", 
                    "models": ["deepseek-chat"],
                    "key_file": "config/api/siliconflow_key.txt"
                }
            },
            "default": {
                "command": "siliconflow.deepseek-chat",
                "script": "openai.gpt-3.5-turbo"
            }
        }
    
    @patch('builtins.open', new_callable=mock_open, read_data="test_api_key")
    @patch('os.path.exists', return_value=True)
    def test_get_api_key(self, mock_path_exists, mock_file):
        """测试获取API密钥"""
        model_manager = ModelManager()
        
        # 测试读取API密钥
        api_key = model_manager.get_api_key("config/api/test_key.txt")
        
        mock_path_exists.assert_called_with("config/api/test_key.txt")
        mock_file.assert_called_with("config/api/test_key.txt", "r", encoding="utf-8")
        self.assertEqual(api_key, "test_api_key")
    
    @patch('os.path.exists', return_value=False)
    def test_get_api_key_missing_file(self, mock_path_exists):
        """测试获取不存在的API密钥文件"""
        model_manager = ModelManager()
        
        # 测试读取不存在的API密钥文件
        api_key = model_manager.get_api_key("config/api/nonexistent_key.txt")
        
        mock_path_exists.assert_called_with("config/api/nonexistent_key.txt")
        self.assertIsNone(api_key)
    
    @patch('yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_command_provider(self, mock_file, mock_yaml_load):
        """测试获取命令提供商配置"""
        # 设置YAML加载返回值
        mock_yaml_load.return_value = self.test_config
        
        model_manager = ModelManager()
        
        # 测试获取命令提供商
        provider = model_manager.get_command_provider()
        
        self.assertEqual(provider["name"], "硅基流动")
        self.assertEqual(provider["model"], "deepseek-chat")
        self.assertEqual(provider["url"], "https://api.siliconflow.com/v1/chat/completions")
        self.assertEqual(provider["key_file"], "config/api/siliconflow_key.txt")
    
    @patch('yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_script_provider(self, mock_file, mock_yaml_load):
        """测试获取脚本提供商配置"""
        # 设置YAML加载返回值
        mock_yaml_load.return_value = self.test_config
        
        model_manager = ModelManager()
        
        # 测试获取脚本提供商
        provider = model_manager.get_script_provider()
        
        self.assertEqual(provider["name"], "OpenAI")
        self.assertEqual(provider["model"], "gpt-3.5-turbo")
        self.assertEqual(provider["url"], "https://api.openai.com/v1/chat/completions")
        self.assertEqual(provider["key_file"], "config/api/openai_key.txt")
    
    @patch('yaml.safe_load')
    @patch('yaml.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_set_default_provider(self, mock_file, mock_yaml_dump, mock_yaml_load):
        """测试设置默认提供商"""
        # 设置YAML加载返回值
        mock_yaml_load.return_value = self.test_config
        
        model_manager = ModelManager()
        
        # 测试设置命令默认提供商
        result = model_manager.set_default_provider("command", "openai.gpt-4")
        
        self.assertTrue(result)
        # 检查YAML dump是否被调用
        mock_yaml_dump.assert_called_once()
        
        # 测试设置无效的提供商
        result = model_manager.set_default_provider("command", "invalid.model")
        
        self.assertFalse(result)
    
    @patch('yaml.safe_load')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_all_providers(self, mock_file, mock_yaml_load):
        """测试获取所有提供商列表"""
        # 设置YAML加载返回值
        mock_yaml_load.return_value = self.test_config
        
        model_manager = ModelManager()
        
        # 测试获取所有提供商
        providers = model_manager.get_all_providers()
        
        self.assertEqual(len(providers), 2)
        self.assertIn("openai", providers)
        self.assertIn("siliconflow", providers)


if __name__ == '__main__':
    unittest.main()
