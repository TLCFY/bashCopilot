#!/usr/bin/env python3
"""
Bash-Copilot 常量配置文件
"""

import os
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent.parent.absolute()

# 历史记录文件
HISTORY_FILE = os.path.join(SCRIPT_DIR, "logs", "bcopilot_history.log")
