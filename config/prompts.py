#!/usr/bin/env python3
"""
Bash-Copilot 提示词模板配置
"""

# 脚本生成提示词模板
SCRIPT_PROMPT_TEMPLATE = """作为专业的Bash脚本开发者，请为以下任务创建一个完整的bash脚本:
    
任务描述: {query}

请生成一个完整的、可执行的bash脚本，包含适当的注释和错误处理。
脚本应该在Ubuntu 20.04环境中运行。

另外，请提供一个简短准确的英文脚本名称（不包含扩展名），用于保存这个脚本文件。
脚本名称应该符合bash命名规范，只包含小写字母、数字和下划线，最多20个字符，能够准确描述脚本功能。

在回复时，请首先提供脚本名称，格式为：[SCRIPT_NAME: 你的脚本名称]，然后再提供完整脚本。

用户环境:
- 当前目录: {current_directory}
- 用户: {username}
- 主机名: {hostname}
- 系统: {ubuntu_version}
"""

# 命令生成提示词模板
COMMAND_PROMPT_TEMPLATE = """你是一个专业的Bash命令生成器，只负责将自然语言转换为Ubuntu 20.04上的bash命令。
只返回一行可直接执行的bash命令，不要有任何解释。如果任务太复杂无法用一行命令完成，
请回复："这个任务无法用单行命令完成，请使用 -script 参数生成完整脚本"。

用户环境:
- 当前目录: {current_directory}
- 用户: {username}
- 主机名: {hostname}
- 系统: {ubuntu_version}

用户请求: {query}
"""

# 添加文件内容的提示模板片段
FILE_CONTENT_PROMPT = """
文件: {filename}
```
{content}
```
"""

# 用于脚本生成时添加文件内容的提示词后缀
SCRIPT_FILE_SUFFIX = "请根据上述文件内容和用户请求生成bash脚本。\n"

# 用于命令生成时添加文件内容的提示词后缀
COMMAND_FILE_SUFFIX = "请生成与这些文件相关的bash命令来完成用户请求。\n"
