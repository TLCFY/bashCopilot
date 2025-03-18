#!/usr/bin/env python3
"""
Bash-Copilot API端点配置
"""
import os
from pathlib import Path

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent.parent.parent.absolute()

# API密钥文件路径
SILICONFLOW_KEY_FILE = os.path.join(SCRIPT_DIR, "config", "api", "siliconflow_key.txt")  # 硅基流动API密钥存储文件
OPENROUTER_KEY_FILE = os.path.join(SCRIPT_DIR, "config", "api", "openrouter_key.txt")  # OpenRouter API密钥存储文件

# API端点配置
COMMAND_API_URL = "https://api.siliconflow.cn/v1/chat/completions"  # 硅基流动API端点
SCRIPT_API_URL = "https://openrouter.ai/api/v1/chat/completions"  # OpenRouter API端点

# 模型配置
COMMAND_MODEL = "Pro/deepseek-ai/DeepSeek-V3"  # 用于生成单行命令的模型
SCRIPT_MODEL = "anthropic/claude-3.7-sonnet"  # 用于生成脚本的模型

# 模型token限制
MODEL_TOKEN_LIMITS = {
    "Pro/deepseek-ai/DeepSeek-V3": 128000,  # DeepSeek-V3的上下文窗口
    "anthropic/claude-3.7-sonnet": 180000,   # Claude 3.7 Sonnet的上下文窗口
}
