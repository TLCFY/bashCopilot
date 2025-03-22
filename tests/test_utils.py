#!/usr/bin/env python3
"""
工具模块测试用例
"""

import unittest
import os
import sys
import platform
from unittest.mock import patch, mock_open, MagicMock

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.context import get_bash_context
from src.utils.file_utils import read_file_contents
from src.utils.token_utils import estimate_tokens


class TestUtils(unittest.TestCase):
    """工具模块测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建测试用临时文件
        self.test_file_path = os.path.join(os.path.dirname(__file__), 'test_utils_file.txt')
        with open(self.test_file_path, 'w') as f:
            f.write('这是测试文件内容\n第二行内容\n' * 5)
    
    def tearDown(self):
        """测试后的清理工作"""
        # 删除测试用临时文件
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    @patch('platform.uname')
    @patch('os.path.expanduser')
    @patch('os.getcwd')
    @patch('getpass.getuser')
    def test_get_bash_context(self, mock_getuser, mock_getcwd, mock_expanduser, mock_uname):
        """测试获取Bash上下文信息"""
        # 模拟系统信息
        mock_getuser.return_value = "testuser"
        mock_getcwd.return_value = "/home/testuser/projects"
        mock_expanduser.return_value = "/home/testuser"
        
        # 模拟Ubuntu版本
        mock_platform = MagicMock()
        mock_platform.system.return_value = "Linux"
        mock_platform.release.return_value = "5.4.0-42-generic"
        mock_uname.return_value = mock_platform
        
        # 应用补丁并测试
        with patch('platform.system', mock_platform.system), \
             patch('platform.release', mock_platform.release):
            
            context = get_bash_context()
            
            self.assertEqual(context["username"], "testuser")
            self.assertEqual(context["current_directory"], "/home/testuser/projects")
            self.assertTrue("hostname" in context)
            self.assertTrue("ubuntu_version" in context or "system_info" in context)
    
    def test_read_file_contents_valid_files(self):
        """测试读取有效文件内容"""
        # 测试读取实际文件
        result = read_file_contents([self.test_file_path], is_script_mode=False)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], self.test_file_path)
        self.assertTrue("这是测试文件内容" in result[0][1])
    
    @patch('os.path.exists', return_value=False)
    def test_read_file_contents_nonexistent_file(self, mock_exists):
        """测试读取不存在的文件"""
        # 测试读取不存在的文件
        with patch('sys.stderr'):  # 屏蔽错误输出
            result = read_file_contents(["nonexistent_file.txt"], is_script_mode=False)
        
        self.assertIsNone(result)
    
    @patch('builtins.open', new_callable=mock_open, read_data="a" * 50000)
    @patch('os.path.exists', return_value=True)
    def test_read_file_contents_large_file(self, mock_exists, mock_file):
        """测试读取大文件时的截断处理"""
        # 模拟读取大文件
        with patch('src.utils.token_utils.estimate_tokens', return_value=10000):
            result = read_file_contents(["large_file.txt"], is_script_mode=False)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        # 检查内容是否被截断
        self.assertLess(len(result[0][1]), 50000)
        self.assertTrue("内容已截断" in result[0][1])
    
    def test_estimate_tokens(self):
        """测试Token估算功能"""
        # 测试空字符串
        self.assertEqual(estimate_tokens(""), 0)
        
        # 测试短文本
        short_text = "这是一个测试文本。"
        self.assertTrue(0 < estimate_tokens(short_text) < 20)
        
        # 测试长文本
        long_text = "这是一个较长的测试文本。" * 100
        self.assertTrue(100 < estimate_tokens(long_text) < 1000)
        
        # 测试特殊字符
        special_text = "测试特殊字符：!@#$%^&*()_+"
        self.assertTrue(estimate_tokens(special_text) > 0)


if __name__ == '__main__':
    unittest.main()
