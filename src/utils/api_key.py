#!/usr/bin/env python3
"""
API密钥读取工具
"""

import sys
from config.api.endpoints import SILICONFLOW_KEY_FILE, OPENROUTER_KEY_FILE

def read_api_key(is_openrouter: bool = False) -> str:
    """
    从文件中读取API密钥

    Args:
        is_openrouter (bool): 是否读取OpenRouter的API密钥
    
    Returns:
        str: API密钥
    """
    filename = OPENROUTER_KEY_FILE if is_openrouter else SILICONFLOW_KEY_FILE
    try:
        with open(filename, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"错误: API密钥文件 '{filename}' 不存在")
        print(f"请创建文件并添加您的API密钥")
        sys.exit(1)
