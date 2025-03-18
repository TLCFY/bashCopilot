#!/usr/bin/env python3
"""
Token 相关工具函数
"""

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
