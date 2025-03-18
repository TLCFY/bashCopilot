#!/usr/bin/env python3
"""
系统上下文收集工具
"""

import os
import subprocess
from typing import Dict

def get_bash_context() -> Dict[str, str]:
    """
    获取bash的当前环境上下文

    Returns:
        Dict[str, str]: 包含当前路径和其他基本信息的字典
    """
    context = {}

    # 获取当前工作目录
    context["current_directory"] = os.getcwd()

    # 获取用户名
    try:
        context["username"] = os.getlogin()
    except:
        context["username"] = "unknown"

    # 获取主机名
    try:
        context["hostname"] = subprocess.getoutput("hostname")
    except:
        context["hostname"] = "unknown"

    # 获取Ubuntu版本
    try:
        context["ubuntu_version"] = subprocess.getoutput("lsb_release -d").replace("Description:", "").strip()
    except:
        context["ubuntu_version"] = "Ubuntu 20.04 (assumed)"

    return context
