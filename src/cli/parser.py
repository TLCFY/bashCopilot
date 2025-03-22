#!/usr/bin/env python3
"""
命令行参数解析模块
"""

import argparse
import sys
from typing import Optional
from argparse import Namespace

def create_config_parser():
    """
    创建配置模式的命令行参数解析器
    
    Returns:
        argparse.ArgumentParser: 专用于config命令的参数解析器
    """
    parser = argparse.ArgumentParser(
        description='Bash-Copilot: 配置管理',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage='bcopilot config ACTION [VALUE]'
    )
    
    parser.add_argument(
        'action',
        choices=['show', 'set', 'add-provider', 'list-providers'],
        help='配置操作'
    )
    parser.add_argument(
        'value',
        nargs='?',
        help='配置值 (用于 set 操作，格式为 "command.provider" 或 "script.provider")'
    )
    
    # 添加一个command字段，以便与查询模式兼容
    parser.set_defaults(command='config')
    
    return parser

def create_query_parser():
    """
    创建查询模式的命令行参数解析器
    
    Returns:
        argparse.ArgumentParser: 参数解析器
    """
    parser = argparse.ArgumentParser(
        description='Bash-Copilot: 将自然语言转换为bash命令或脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  bcopilot "查找大于100MB的文件"
  bcopilot -script "备份我的主目录"
  bcopilot -filename config.json log.txt "处理这些文件"
        """
    )
    
    # 主命令参数
    parser.add_argument('-script', action='store_true', help='生成脚本而不是单行命令')
    parser.add_argument('-help', action='help', help='显示此帮助信息并退出')
    parser.add_argument('-filename', type=str, nargs='+', help='在提示中包含指定文件的内容')
    parser.add_argument('query', nargs='?', help='自然语言查询')
    
    # 设置默认的command值为None，表示这是查询模式而非config模式
    parser.set_defaults(command=None)
    
    return parser

def create_help_parser():
    """
    创建帮助信息解析器，用于显示总体帮助
    
    Returns:
        argparse.ArgumentParser: 帮助信息解析器
    """
    parser = argparse.ArgumentParser(
        description='Bash-Copilot: 将自然语言转换为bash命令或脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
用法:
  bcopilot "自然语言查询"         # 生成bash命令
  bcopilot -script "查询"        # 生成bash脚本
  bcopilot -filename file.txt "查询"  # 包含文件内容
  bcopilot config show          # 显示配置
  bcopilot config set command.openai  # 设置配置
        """
    )
    return parser

def parse_arguments():
    """
    解析命令行参数，使用不同的解析器处理不同的命令模式
    
    Returns:
        argparse.Namespace: 解析后的命令行参数
    """
    # 获取命令行参数
    args = sys.argv[1:]
    
    # 如果没有参数，显示帮助
    if not args:
        parser = create_help_parser()
        parser.print_help()
        sys.exit(1)
    
    # 检查第一个参数是否是"config"
    if args[0] == 'config':
        # 使用config专用解析器
        config_parser = create_config_parser()
        return config_parser.parse_args(args[1:])  # 跳过"config"参数
    else:
        # 使用查询解析器
        query_parser = create_query_parser()
        parsed_args = query_parser.parse_args(args)
        
        # 检查是否提供了查询
        if not parsed_args.query:
            query_parser.print_help()
            sys.exit(1)
        
        return parsed_args
