#!/usr/bin/env python3
"""
Token 相关工具函数
"""

from src.config.model_manager import ModelManager

def get_model_token_limit(model_name: str) -> int:
    """
    获取指定模型的token限制
    
    Args:
        model_name (str): 模型名称
    
    Returns:
        int: 模型的token限制
    """
    manager = ModelManager()
    token_limits = manager.get_model_token_limits()
    
    # 如果找到精确匹配，直接返回
    if model_name in token_limits:
        return token_limits[model_name]
    
    # 如果没有精确匹配，尝试部分匹配
    for model, limit in token_limits.items():
        if model_name in model or model in model_name:
            return limit
    
    # 默认值
    return 100000

def estimate_tokens(text: str) -> int:
    """
    估算文本的tokens数量

    Args:
        text (str): 输入文本
    
    Returns:
        int: 预估的tokens数量
    """
    # 一般英文中平均一个token约等于4个字符
    # 中文和其他非拉丁语系通常一个字符就是一个token

    # 计算非ASCII字符数（如中文）
    non_ascii_count = sum(1 for char in text if ord(char) > 127)

    # 计算ASCII字符数并除以4（估算英文tokens）
    ascii_count = len(text) - non_ascii_count
    ascii_tokens = ascii_count / 4

    # 非ASCII字符按1:1计算tokens
    return int(ascii_tokens + non_ascii_count)
