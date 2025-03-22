#!/usr/bin/env python3
"""
Bash-Copilot 启动脚本
此脚本可以从项目根目录运行，不会遇到模块导入问题
"""

import sys
import os

# 确保当前目录在Python模块搜索路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并运行main函数
from src.main import main

if __name__ == "__main__":
    main()
