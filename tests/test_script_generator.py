#!/usr/bin/env python3
"""
脚本生成器测试用例
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generators.script_generator import handle_script_generation
from src.generators.base_generator import generate_bash_command


class TestScriptGenerator(unittest.TestCase):
    """脚本生成器测试类"""
    
    @patch('src.generators.base_generator.generate_bash_command')
    @patch('builtins.print')
    @patch('src.log.history.append_to_history')
    def test_handle_script_generation_success(self, mock_history, mock_print, mock_generate):
        """测试成功生成脚本的情况"""
        # 模拟脚本内容
        script_content = """#!/bin/bash
# 系统监控脚本
# 用于监控CPU和内存使用情况

while true; do
    echo "======= 系统状态 ======="
    date
    echo "CPU使用率:"
    top -b -n 1 | head -n 5
    echo "内存使用情况:"
    free -h
    echo "磁盘使用情况:"
    df -h
    sleep 5
done
"""
        # 模拟成功生成脚本
        mock_generate.return_value = (True, script_content)
        
        # 模拟上下文
        context = {
            "current_directory": "/home/user",
            "username": "testuser",
            "hostname": "testhost",
            "ubuntu_version": "20.04"
        }
        
        # 使用临时目录进行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            # 将临时目录添加到sys.path
            old_path = sys.path.copy()
            sys.path.insert(0, temp_dir)
            
            try:
                # 测试脚本生成
                with patch('src.generators.script_generator.os.getcwd', return_value=temp_dir):
                    handle_script_generation(
                        "创建一个系统监控脚本", 
                        context, 
                        None,
                        None
                    )
                
                # 验证生成脚本的调用
                mock_generate.assert_called_once()
                mock_history.assert_called_once()
                
                # 检查是否有打印成功消息
                success_calls = [call for call in mock_print.call_args_list if "已创建脚本" in str(call)]
                self.assertGreater(len(success_calls), 0)
                
            finally:
                # 恢复原始路径
                sys.path = old_path
    
    @patch('src.generators.base_generator.generate_bash_command')
    @patch('builtins.print')
    def test_handle_script_generation_failure(self, mock_print, mock_generate):
        """测试脚本生成失败的情况"""
        # 模拟生成失败
        mock_generate.return_value = (False, "API错误: 请求超时")
        
        # 模拟上下文
        context = {
            "current_directory": "/home/user",
            "username": "testuser",
            "hostname": "testhost",
            "ubuntu_version": "20.04"
        }
        
        # 测试脚本生成失败
        handle_script_generation("创建一个系统监控脚本", context, None, None)
        
        # 验证生成脚本的调用
        mock_generate.assert_called_once()
        
        # 检查是否有打印错误消息
        error_calls = [call for call in mock_print.call_args_list if "错误" in str(call)]
        self.assertGreater(len(error_calls), 0)
    
    @patch('src.generators.base_generator.generate_bash_command')
    @patch('builtins.print')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('os.chmod')
    def test_script_file_creation(self, mock_chmod, mock_open, mock_print, mock_generate):
        """测试脚本文件的创建和权限设置"""
        # 模拟脚本内容
        script_content = """#!/bin/bash
echo "这是测试脚本"
"""
        # 模拟成功生成脚本
        mock_generate.return_value = (True, script_content)
        
        # 模拟上下文
        context = {
            "current_directory": "/home/user",
            "username": "testuser",
            "hostname": "testhost",
            "ubuntu_version": "20.04"
        }
        
        # 使用临时目录进行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            # 测试脚本生成
            with patch('src.generators.script_generator.os.getcwd', return_value=temp_dir):
                handle_script_generation(
                    "创建一个简单的测试脚本", 
                    context, 
                    None,
                    None
                )
            
            # 验证文件创建
            mock_open.assert_called_once()
            
            # 验证权限设置 (0o755 = rwxr-xr-x)
            mock_chmod.assert_called_once()
            self.assertEqual(mock_chmod.call_args[0][1], 0o755)
    
    @patch('src.generators.base_generator.generate_bash_command')
    @patch('builtins.print')
    def test_script_generation_with_file_context(self, mock_print, mock_generate):
        """测试使用文件上下文生成脚本"""
        # 模拟脚本内容
        script_content = """#!/bin/bash
# 处理配置文件的脚本
CONFIG_FILE="test_config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件不存在" >&2
    exit 1
fi

echo "正在处理配置文件..."
cat "$CONFIG_FILE" | jq '.'
echo "处理完成"
"""
        # 模拟成功生成脚本
        mock_generate.return_value = (True, script_content)
        
        # 模拟上下文
        context = {
            "current_directory": "/home/user",
            "username": "testuser",
            "hostname": "testhost",
            "ubuntu_version": "20.04"
        }
        
        # 模拟文件内容
        file_contents = [
            ("test_config.json", '{"name": "test", "value": 123}')
        ]
        
        # 使用临时目录进行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            # 测试脚本生成
            with patch('src.generators.script_generator.os.getcwd', return_value=temp_dir):
                handle_script_generation(
                    "创建一个处理配置文件的脚本", 
                    context, 
                    file_contents,
                    ["test_config.json"]
                )
            
            # 验证生成脚本的调用
            mock_generate.assert_called_once_with(
                "创建一个处理配置文件的脚本", 
                context, 
                is_script=True, 
                file_contents=file_contents
            )


if __name__ == '__main__':
    unittest.main()
