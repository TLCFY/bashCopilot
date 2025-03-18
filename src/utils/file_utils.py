#!/usr/bin/env python3
"""
文件处理工具
"""

import sys
from typing import List, Tuple, Optional
from src.utils.token_utils import estimate_tokens
from config.api.endpoints import COMMAND_MODEL, SCRIPT_MODEL, MODEL_TOKEN_LIMITS

def read_file_contents(filenames: List[str], is_script_mode: bool) -> Optional[List[Tuple[str, str]]]:
    """
    读取指定文件的内容，并检查token限制

    Args:
        filenames (List[str]): 需要读取的文件列表
        is_script_mode (bool): 是否为脚本生成模式
    
    Returns:
        Optional[List[Tuple[str, str]]]: 文件内容列表，每项为(文件名, 内容)的元组。如果超出token限制或出错则返回None
    """
    # 选择对应的模型和token限制
    model = SCRIPT_MODEL if is_script_mode else COMMAND_MODEL
    token_limit = MODEL_TOKEN_LIMITS[model]
    
    # 为系统提示和模型回复预留空间
    available_tokens = token_limit - 2000
    
    file_contents = []
    total_tokens = 500  # 环境上下文的token估算
    
    # 添加查询的tokens（估算值）
    query_tokens = 200  # 假设查询平均不超过200 tokens
    total_tokens += query_tokens
    
    for filename in filenames:
        try:
            with open(filename, 'r') as f:
                content = f.read()
            file_tokens = estimate_tokens(content)
            total_tokens += file_tokens
            file_contents.append((filename, content))
            print(f"包含文件内容: {filename} (预估 {file_tokens} tokens)")
        except Exception as e:
            print(f"读取文件 '{filename}' 出错: {str(e)}")
            return None
    
    # 在读取所有文件后，检查token总量
    if total_tokens > 6000:
        print(f"警告: 预估token消耗({total_tokens})可能过大，这可能会导致较高的API调用成本。")
        confirm = input("是否继续操作？(y/N): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            sys.exit(0)
    
    # 检查是否已超出token限制
    if total_tokens > available_tokens:
        print(f"错误: 文件内容太大，预估超过{total_tokens}个tokens")
        print(f"超出了{model}模型的限制({available_tokens} tokens)")
        print("请减少文件数量或使用更小的文件")
        return None
    
    return file_contents
