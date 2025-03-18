#!/usr/bin/env python3
"""
Bash-Copilot 命令行工具
主入口脚本
"""

import sys
import os

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入并执行主模块
from src.main import main

if __name__ == "__main__":
    main()
