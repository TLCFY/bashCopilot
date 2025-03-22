#!/usr/bin/env python3
"""
配置命令处理模块测试用例
"""

import unittest
import os
import sys
import yaml
from unittest.mock import patch, mock_open, MagicMock

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cli.config_commands import handle_config_command


class TestConfigCommands(unittest.TestCase):
    """配置命令处理模块测试类"""
    
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
    
    @patch('src.config.model_manager.ModelManager.get_command_provider')
    @patch('src.config.model_manager.ModelManager.get_script_provider')
    @patch('builtins.print')
    def test_handle_config_show(self, mock_print, mock_get_script, mock_get_command):
        """测试显示配置命令"""
        # 模拟提供商数据
        mock_get_command.return_value = {
            "name": "硅基流动",
            "model": "deepseek-chat",
            "url": "https://api.siliconflow.com/v1/chat/completions",
            "key_file": "config/api/siliconflow_key.txt"
        }
        mock_get_script.return_value = {
            "name": "OpenAI",
            "model": "gpt-3.5-turbo",
            "url": "https://api.openai.com/v1/chat/completions",
            "key_file": "config/api/openai_key.txt"
        }
        
        # 创建参数命名空间
        args = MagicMock()
        args.action = "show"
        
        # 测试配置显示
        handle_config_command(args)
        
        # 验证打印调用
        self.assertTrue(mock_print.called)
        command_print = False
        script_print = False
        for call in mock_print.call_args_list:
            call_str = str(call)
            if "命令生成" in call_str and "硅基流动" in call_str:
                command_print = True
            if "脚本生成" in call_str and "OpenAI" in call_str:
                script_print = True
        
        self.assertTrue(command_print)
        self.assertTrue(script_print)
    
    @patch('src.config.model_manager.ModelManager.set_default_provider')
    @patch('builtins.print')
    def test_handle_config_set_success(self, mock_print, mock_set_default):
        """测试成功设置配置命令"""
        # 模拟成功设置
        mock_set_default.return_value = True
        
        # 创建参数命名空间
        args = MagicMock()
        args.action = "set"
        args.value = "command.openai.gpt-4"
        
        # 测试配置设置
        handle_config_command(args)
        
        # 验证设置调用
        mock_set_default.assert_called_once_with("command", "openai.gpt-4")
        
        # 验证打印成功消息
        success_prints = [call for call in mock_print.call_args_list if "成功" in str(call)]
        self.assertGreater(len(success_prints), 0)
    
    @patch('src.config.model_manager.ModelManager.set_default_provider')
    @patch('builtins.print')
    def test_handle_config_set_failure(self, mock_print, mock_set_default):
        """测试设置配置失败命令"""
        # 模拟设置失败
        mock_set_default.return_value = False
        
        # 创建参数命名空间
        args = MagicMock()
        args.action = "set"
        args.value = "command.invalid.model"
        
        # 测试配置设置失败
        handle_config_command(args)
        
        # 验证设置调用
        mock_set_default.assert_called_once_with("command", "invalid.model")
        
        # 验证打印错误消息
        error_prints = [call for call in mock_print.call_args_list if "错误" in str(call)]
        self.assertGreater(len(error_prints), 0)
    
    @patch('src.config.model_manager.ModelManager.set_default_provider')
    @patch('builtins.print')
    def test_handle_config_set_invalid_format(self, mock_print, mock_set_default):
        """测试设置配置格式无效命令"""
        # 创建参数命名空间
        args = MagicMock()
        args.action = "set"
        args.value = "invalid_format"
        
        # 测试配置设置无效格式
        handle_config_command(args)
        
        # 验证未调用设置
        mock_set_default.assert_not_called()
        
        # 验证打印格式错误消息
        format_error_prints = [call for call in mock_print.call_args_list if "格式" in str(call)]
        self.assertGreater(len(format_error_prints), 0)
    
    @patch('src.config.model_manager.ModelManager.get_all_providers')
    @patch('builtins.print')
    def test_handle_config_list_providers(self, mock_print, mock_get_providers):
        """测试列出所有提供商命令"""
        # 模拟提供商列表
        mock_get_providers.return_value = {
            "openai": {
                "name": "OpenAI",
                "models": ["gpt-3.5-turbo", "gpt-4"]
            },
            "siliconflow": {
                "name": "硅基流动",
                "models": ["deepseek-chat"]
            }
        }
        
        # 创建参数命名空间
        args = MagicMock()
        args.action = "list-providers"
        
        # 测试列出提供商
        handle_config_command(args)
        
        # 验证获取提供商调用
        mock_get_providers.assert_called_once()
        
        # 验证打印提供商信息
        provider_prints = [call for call in mock_print.call_args_list if "OpenAI" in str(call) or "硅基流动" in str(call)]
        self.assertGreater(len(provider_prints), 0)
    
    @patch('builtins.input')
    @patch('yaml.safe_dump')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_handle_config_add_provider(self, mock_print, mock_file, mock_yaml_dump, mock_input):
        """测试添加提供商命令"""
        # 模拟用户输入
        mock_input.side_effect = [
            "gemini",  # 提供商ID
            "Google Gemini",  # 提供商名称
            "https://api.google.com/v1/chat/completions",  # API URL
            "gemini-pro",  # 模型名称
            "n",  # 不添加更多模型
            "config/api/gemini_key.txt",  # API密钥文件路径
            "y"  # 确认添加
        ]
        
        # 创建参数命名空间
        args = MagicMock()
        args.action = "add-provider"
        
        # 测试添加提供商
        with patch('src.cli.config_commands.yaml.safe_load', return_value=self.test_config):
            with patch('os.path.exists', return_value=True):
                handle_config_command(args)
        
        # 验证YAML保存调用
        mock_yaml_dump.assert_called_once()
        
        # 验证打印成功消息
        success_prints = [call for call in mock_print.call_args_list if "成功" in str(call)]
        self.assertGreater(len(success_prints), 0)


if __name__ == '__main__':
    unittest.main()
