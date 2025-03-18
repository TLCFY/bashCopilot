#!/usr/bin/env python3
"""
Bash-Copilot: 将自然语言转换为bash命令的命令行工具

环境要求:
- Python 3.6+
- requests库
- Ubuntu 20.04

用法:
$ bcopilot "如何查找最大的5个文件"     # 仅生成单行命令
$ bcopilot -script "如何查找系统中的大文件"  # 生成完整脚本
$ bcopilot -filename file1.txt file2.json "处理这些文件"  # 包含文件内容作为上下文
$ bcopilot -help  # 显示帮助信息
"""

import os
import sys
import json
from typing import Dict, Tuple, List, Optional

from config.api.endpoints import COMMAND_MODEL, SCRIPT_MODEL, MODEL_TOKEN_LIMITS
from src.cli.parser import parse_arguments
from src.utils.context import get_bash_context
from src.utils.file_utils import read_file_contents
from src.generators.command_generator import handle_command_generation
from src.generators.script_generator import handle_script_generation

def main():
    # 解析命令行参数
    args = parse_arguments()

    # 获取bash环境上下文
    context = get_bash_context()

    # 根据参数决定是否直接生成脚本
    is_script_mode = args.script

    # 读取文件内容（如果指定了-filename）
    file_contents = None
    if args.filename:
        file_contents = read_file_contents(args.filename, is_script_mode)
        if file_contents is None:
            sys.exit(1)

    # 根据模式调用不同的生成器
    if is_script_mode:
        handle_script_generation(
            args.query, 
            context, 
            file_contents,
            args.filename
        )
    else:
        handle_command_generation(
            args.query, 
            context, 
            file_contents,
            args.filename
        )

if __name__ == "__main__":
    main()
