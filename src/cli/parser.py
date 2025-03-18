#!/usr/bin/env python3
"""
命令行参数解析模块
"""

import argparse
import sys
from typing import Optional

def create_argument_parser():
    """
    创建命令行参数解析器

    Returns:
        argparse.ArgumentParser: 配置好的参数解析器
    """
    parser = argparse.ArgumentParser(
        description='Bash-Copilot: 将自然语言转换为bash命令或脚本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  bcopilot "查找大于100MB的文件"
  bcopilot -script "备份我的主目录"
  bcopilot -filename config.json log.txt "处理这些文件"
  bcopilot config show
  bcopilot config set command.openai
        """
    )
    
    # 创建子解析器
    subparsers = parser.add_subparsers(dest='command')
    
    # 添加配置子命令
    config_parser = subparsers.add_parser('config', help='管理模型配置')
    config_parser.add_argument(
        'action',
        choices=['show', 'set', 'add-provider', 'list-providers'],
        help='配置操作'
    )
    config_parser.add_argument(
        'value',
        nargs='?',
        help='配置值 (用于 set 操作，格式为 "command.provider" 或 "script.provider")'
    )
    
    # 主命令参数
    parser.add_argument('query', nargs='?', help='自然语言查询')
    parser.add_argument('-script', action='store_true', help='生成脚本而不是单行命令')
    parser.add_argument('-help', action='help', help='显示此帮助信息并退出')
    parser.add_argument('-filename', type=str, nargs='+', help='在提示中包含指定文件的内容')

    return parser

def parse_arguments():
    """
    解析命令行参数

    Returns:
        argparse.Namespace: 解析后的命令行参数
    """
    parser = create_argument_parser()
    args = parser.parse_args()

    # 检查是否提供了查询(仅在非config命令模式下需要)
    if not args.command and not args.query:
        parser.print_help()
        sys.exit(1)

    return args
