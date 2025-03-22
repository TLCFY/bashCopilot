#!/usr/bin/env python3
"""
Bash-Copilot 测试用例
"""

import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cli.parser import parse_arguments
from src.config.model_manager import ModelManager
from src.utils.context import get_bash_context
from src.utils.file_utils import read_file_contents
from src.generators.base_generator import generate_bash_command
from src.generators.command_generator import handle_command_generation
from src.generators.script_generator import handle_script_generation


class MockResponse:
    """模拟API响应的类"""
    
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)
    
    def json(self):
        return self.json_data


class TestBashCopilot(unittest.TestCase):
    """Bash-Copilot 项目测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试用临时文件
        self.test_file_path = os.path.join(os.path.dirname(__file__), 'test_file.txt')
        with open(self.test_file_path, 'w') as f:
            f.write('这是一个测试文件\n包含一些用于测试的内容')
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除测试用临时文件
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    @patch('sys.argv', ['bcopilot', '查找当前目录下最大的5个文件'])
    def test_argument_parsing_query_mode(self):
        """测试查询模式的参数解析"""
        args = parse_arguments()
        self.assertEqual(args.query, '查找当前目录下最大的5个文件')
        self.assertFalse(args.script)
        self.assertIsNone(args.filename)
        self.assertIsNone(args.command)
    
    @patch('sys.argv', ['bcopilot', '-script', '备份MySQL数据库'])
    def test_argument_parsing_script_mode(self):
        """测试脚本模式的参数解析"""
        args = parse_arguments()
        self.assertEqual(args.query, '备份MySQL数据库')
        self.assertTrue(args.script)
        self.assertIsNone(args.filename)
        self.assertIsNone(args.command)
    
    @patch('sys.argv', ['bcopilot', 'config', 'show'])
    def test_argument_parsing_config_mode(self):
        """测试配置模式的参数解析"""
        args = parse_arguments()
        self.assertEqual(args.command, 'config')
        self.assertEqual(args.action, 'show')
        self.assertIsNone(args.value)
    
    @patch('requests.post')
    def test_command_generation(self, mock_post):
        """测试命令生成功能"""
        # 模拟API响应
        mock_response = MockResponse({
            "choices": [
                {"message": {"content": "find . -type f -size +100M -exec ls -lh {} \\;"}}
            ]
        }, 200)
        mock_post.return_value = mock_response
        
        # 模拟环境上下文
        context = {
            "current_directory": "/home/user",
            "username": "testuser",
            "hostname": "testhost",
            "ubuntu_version": "20.04"
        }
        
        # 测试命令生成
        success, result = generate_bash_command("查找大于100MB的文件", context)
        
        self.assertTrue(success)
        self.assertEqual(result, "find . -type f -size +100M -exec ls -lh {} \\;")
    
    @patch('requests.post')
    def test_script_generation(self, mock_post):
        """测试脚本生成功能"""
        # 模拟API响应
        script_content = """#!/bin/bash
# 备份MySQL数据库脚本

# 定义变量
DB_USER="root"
DB_PASS="password"
DB_NAME="mydb"
BACKUP_DIR="/home/user/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 执行备份
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > "$BACKUP_DIR/${DB_NAME}_$DATE.sql"

# 检查备份是否成功
if [ $? -eq 0 ]; then
    echo "备份成功: $BACKUP_DIR/${DB_NAME}_$DATE.sql"
else
    echo "备份失败" >&2
    exit 1
fi
"""
        mock_response = MockResponse({
            "choices": [
                {"message": {"content": script_content}}
            ]
        }, 200)
        mock_post.return_value = mock_response
        
        # 模拟环境上下文
        context = {
            "current_directory": "/home/user",
            "username": "testuser",
            "hostname": "testhost",
            "ubuntu_version": "20.04"
        }
        
        # 测试脚本生成
        success, result = generate_bash_command("备份MySQL数据库", context, is_script=True)
        
        self.assertTrue(success)
        self.assertEqual(result, script_content)
    
    @patch('requests.post')
    def test_file_context_command_generation(self, mock_post):
        """测试带文件上下文的命令生成"""
        # 模拟API响应
        mock_response = MockResponse({
            "choices": [
                {"message": {"content": "grep -n '测试' test_file.txt"}}
            ]
        }, 200)
        mock_post.return_value = mock_response
        
        # 模拟环境上下文
        context = {
            "current_directory": "/home/user",
            "username": "testuser",
            "hostname": "testhost",
            "ubuntu_version": "20.04"
        }
        
        # 准备文件内容
        file_contents = [
            (self.test_file_path, "这是一个测试文件\n包含一些用于测试的内容")
        ]
        
        # 测试带文件上下文的命令生成
        success, result = generate_bash_command("查找文件中的'测试'字样", context, file_contents=file_contents)
        
        self.assertTrue(success)
        self.assertEqual(result, "grep -n '测试' test_file.txt")
    
    @patch('requests.post')
    def test_api_error_handling(self, mock_post):
        """测试API错误处理"""
        # 模拟API错误响应
        mock_response = MockResponse({
            "error": {
                "message": "API密钥无效"
            }
        }, 401)
        mock_post.return_value = mock_response
        
        # 模拟环境上下文
        context = {
            "current_directory": "/home/user",
            "username": "testuser",
            "hostname": "testhost",
            "ubuntu_version": "20.04"
        }
        
        # 测试错误处理
        success, result = generate_bash_command("查找大文件", context)
        
        self.assertFalse(success)
        self.assertIn("API错误", result)
        self.assertIn("API密钥无效", result)
    
    @patch('src.config.model_manager.ModelManager.get_command_provider')
    @patch('src.config.model_manager.ModelManager.get_api_key')
    def test_missing_api_key(self, mock_get_api_key, mock_get_command_provider):
        """测试缺少API密钥的情况"""
        # 模拟配置和缺少API密钥
        mock_get_command_provider.return_value = {
            "name": "openai",
            "url": "https://api.openai.com/v1/chat/completions",
            "model": "gpt-3.5-turbo",
            "key_file": "config/api/openai_key.txt"
        }
        mock_get_api_key.return_value = None
        
        # 模拟环境上下文
        context = {
            "current_directory": "/home/user",
            "username": "testuser",
            "hostname": "testhost",
            "ubuntu_version": "20.04"
        }
        
        # 测试缺少API密钥的错误处理
        success, result = generate_bash_command("查找大文件", context)
        
        self.assertFalse(success)
        self.assertIn("未找到API密钥", result)
    
    def test_model_manager(self):
        """测试模型管理器功能"""
        # 因为需要依赖真实配置文件，这里我们只测试实例化
        model_manager = ModelManager()
        self.assertIsNotNone(model_manager)
        
        # 这部分可以根据实际情况添加更多测试，但需要mock配置文件
        # 或者在测试环境中创建测试用的配置文件


if __name__ == '__main__':
    unittest.main()
