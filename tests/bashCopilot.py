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
import argparse
import subprocess
import requests
from typing import Dict, Tuple, List, Optional
from pathlib import Path
from datetime import datetime

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent.absolute()

# 配置信息
API_KEY_FILE = os.path.join(SCRIPT_DIR.parent, "config", "api_key.txt")  # 硅基流动API密钥存储文件
OPENROUTER_KEY_FILE = os.path.join(SCRIPT_DIR.parent, "config", "openrouter_key.txt")  # OpenRouter API密钥存储文件

# API端点配置
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"  # 硅基流动API端点
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"  # OpenRouter API端点

# 模型配置
COMMAND_MODEL = "Pro/deepseek-ai/DeepSeek-V3"  # 用于生成单行命令的模型
SCRIPT_MODEL = "anthropic/claude-3.7-sonnet"  # 正确的Claude 3.7 Sonnet模型名称

# 模型token限制
MODEL_TOKEN_LIMITS = {
    COMMAND_MODEL: 128000,  # DeepSeek-V3的上下文窗口
    SCRIPT_MODEL: 180000,   # Claude 3.7 Sonnet的上下文窗口
}

# 历史记录文件
HISTORY_FILE = os.path.join(SCRIPT_DIR.parent, "logs", "bcopilot_history.log")


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


def read_api_key(is_openrouter: bool = False) -> str:
    """
    从文件中读取API密钥

    Args:
        is_openrouter (bool): 是否读取OpenRouter的API密钥
    
    Returns:
        str: API密钥
    """
    filename = OPENROUTER_KEY_FILE if is_openrouter else API_KEY_FILE
    try:
        with open(filename, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"错误: API密钥文件 '{filename}' 不存在")
        print(f"请创建文件并添加您的API密钥")
        sys.exit(1)


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


def append_to_history(query: str, answer: str, type_name: str = "command", 
                     script_path: Optional[str] = None, 
                     filenames: Optional[List[str]] = None) -> None:
    """
    将查询和结果追加到历史记录文件

    Args:
        query (str): 用户的查询
        answer (str): 生成的答案
        type_name (str): 记录类型 (command/script)
        script_path (str, optional): 脚本保存路径，仅在type_name为"script"时有效
        filenames (List[str], optional): 包含在提示中的文件名列表
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 准备要写入的内容
    entry = f"""
=== {timestamp} [{type_name}] ===
查询: {query}
"""
    # 如果指定了文件，添加文件信息
    if filenames:
        entry += f"相关文件: {', '.join(filenames)}\n"
    
    entry += f"结果: {answer}\n"

    # 如果是脚本类型且提供了脚本路径，则添加脚本路径信息
    if type_name == "script" and script_path:
        entry += f"脚本位置: {script_path}\n"
    
    entry += f"{'=' * 60}\n"

    # 追加到历史文件
    with open(HISTORY_FILE, 'a') as f:
        f.write(entry)


def generate_bash_command(query: str, context: Dict[str, str], 
                          is_script: bool = False,
                          file_contents: Optional[List[Tuple[str, str]]] = None) -> Tuple[bool, str]:
    """
    通过API将自然语言查询转换为bash命令或脚本

    Args:
        query (str): 用户的自然语言查询
        context (Dict[str, str]): bash环境上下文
        is_script (bool): 是否生成脚本而不是单行命令
        file_contents (List[Tuple[str, str]], optional): 文件内容列表，每项为(文件名, 内容)的元组
    
    Returns:
        Tuple[bool, str]: (是否成功, 生成的bash命令或错误消息)
    """
    # 根据需求选择不同的API和模型
    if is_script:
        # 脚本生成使用OpenRouter的Claude 3.7 Sonnet
        api_url = OPENROUTER_API_URL
        model = SCRIPT_MODEL
        api_key = read_api_key(is_openrouter=True)
        print("正在使用 Claude 3.7 Sonnet 模型生成脚本，可能需要1-2分钟，请等待。")
        timeout = 120
    else:
        # 命令生成使用硅基流动的DeepSeek-V3
        api_url = SILICONFLOW_API_URL
        model = COMMAND_MODEL
        api_key = read_api_key(is_openrouter=False)
        timeout = 30

    # 构建提示词
    if is_script:
        prompt_text = f"""作为专业的Bash脚本开发者，请为以下任务创建一个完整的bash脚本:
    
任务描述: {query}

请生成一个完整的、可执行的bash脚本，包含适当的注释和错误处理。
脚本应该在Ubuntu 20.04环境中运行。

另外，请提供一个简短准确的英文脚本名称（不包含扩展名），用于保存这个脚本文件。
脚本名称应该符合bash命名规范，只包含小写字母、数字和下划线，最多20个字符，能够准确描述脚本功能。

在回复时，请首先提供脚本名称，格式为：[SCRIPT_NAME: 你的脚本名称]，然后再提供完整脚本。

用户环境:
- 当前目录: {context['current_directory']}
- 用户: {context['username']}
- 主机名: {context['hostname']}
- 系统: {context['ubuntu_version']}
"""
        # 添加文件内容（如果有）
        if file_contents:
            prompt_text += "\n相关文件内容:\n"
            for filename, content in file_contents:
                prompt_text += f"""
文件: {filename}
```
{content}
```

"""
            prompt_text += "请根据上述文件内容和用户请求生成bash脚本。\n"
    else:
        prompt_text = f"""你是一个专业的Bash命令生成器，只负责将自然语言转换为Ubuntu 20.04上的bash命令。
只返回一行可直接执行的bash命令，不要有任何解释。如果任务太复杂无法用一行命令完成，
请回复："这个任务无法用单行命令完成，请使用 -script 参数生成完整脚本"。

用户环境:
- 当前目录: {context['current_directory']}
- 用户: {context['username']}
- 主机名: {context['hostname']}
- 系统: {context['ubuntu_version']}

用户请求: {query}
"""
        # 添加文件内容（如果有）
        if file_contents:
            prompt_text += "\n相关文件内容:\n"
            for filename, content in file_contents:
                prompt_text += f"""
文件: {filename}
```
{content}
```

"""
            prompt_text += "请生成与这些文件相关的bash命令来完成用户请求。\n"

    try:
        if is_script:
            # OpenRouter请求 - 按照Claude 3.7 Sonnet的正确格式
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://bash-copilot.local",
                "X-Title": "Bash-Copilot"
            }
        
            # 使用Claude 3.7 Sonnet的消息格式
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        }
                    ]
                }
            ]
        
            # OpenRouter特定的请求格式
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 4000
            }
        
            # 发送请求并使用json.dumps确保正确的JSON格式
            response = requests.post(
                url=api_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=timeout
            )
        
        else:
            # 硅基流动请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        
            # 标准的OpenAI格式消息
            messages = [{"role": "user", "content": prompt_text}]
        
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 200
            }
        
            response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
    
        # 检查响应状态
        if response.status_code != 200:
            try:
                error_detail = response.json()
                error_message = error_detail.get("error", {}).get("message", "未知错误")
                return False, f"API错误 ({response.status_code}): {error_message}"
            except:
                return False, f"API错误 ({response.status_code}): {response.text}"
    
        # 处理成功响应
        result = response.json()
    
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
        
            # 如果内容是列表格式（Claude 3.7 特殊格式），需要提取文本
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                content = "".join(text_parts)
        
            return True, content.strip()
        else:
            return False, "API响应格式不正确"
        
    except requests.exceptions.RequestException as e:
        return False, f"API请求错误: {str(e)}"
    except json.JSONDecodeError:
        return False, f"无法解析API响应: {response.text if 'response' in locals() else '未知响应'}"
    except Exception as e:
        return False, f"未知错误: {str(e)}"


def create_script_file(content: str, query: str) -> str:
    """
    创建可执行脚本文件，保存在用户当前工作目录

    Args:
        content (str): 脚本内容
        query (str): 用户的原始查询，用于生成默认文件名
    
    Returns:
        str: 脚本文件路径
    """
    # 尝试从内容中提取脚本名称
    script_name = None
    if "[SCRIPT_NAME:" in content:
        try:
            start = content.find("[SCRIPT_NAME:") + 13
            end = content.find("]", start)
            if end > start:
                script_name = content[start:end].strip()
                # 清理名称，确保只包含有效字符
                script_name = "".join(c for c in script_name if c.isalnum() or c == '_').lower()
                # 移除从内容中提取的脚本名称部分
                content = content[end+1:].strip()
        except:
            script_name = None

    # 如果没有成功提取脚本名称，使用默认名称
    if not script_name or len(script_name) < 2:
        # 默认名称: script_日期时间
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_name = f"script_{timestamp}"

    # 提取代码块，如果输出包含Markdown代码块
    if "```bash" in content or "```sh" in content:
        try:
            start = content.find("```") + 3
            start = content.find("\n", start) + 1
            end = content.find("```", start)
            if end > start:
                content = content[start:end].strip()
        except:
            # 如果提取失败，则使用原始内容
            pass

    # 确保文件名不重复
    script_path = os.path.join(os.getcwd(), f"{script_name}.sh")
    counter = 1
    while os.path.exists(script_path):
        script_path = os.path.join(os.getcwd(), f"{script_name}_{counter}.sh")
        counter += 1

    with open(script_path, 'w') as f:
        f.write("#!/bin/bash\n\n")
        f.write("# 由Bash-Copilot生成的脚本\n")
        f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 查询内容: {query}\n\n")
        f.write(content)

    # 使脚本可执行
    os.chmod(script_path, 0o755)

    return script_path


def main():
    # 创建命令行参数解析器
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
    parser.add_argument('query', nargs='?', help='自然语言查询')
    parser.add_argument('-script', action='store_true', help='生成脚本而不是单行命令')
    parser.add_argument('-help', action='help', help='显示此帮助信息并退出')
    parser.add_argument('-filename', type=str, nargs='+', help='在提示中包含指定文件的内容')

    # 解析命令行参数
    args = parser.parse_args()

    # 检查是否提供了查询
    if not args.query:
        parser.print_help()
        sys.exit(1)

    # 获取bash环境上下文
    context = get_bash_context()

    # 根据参数决定是否直接生成脚本
    is_script_mode = args.script

    # 选择模型
    model = SCRIPT_MODEL if is_script_mode else COMMAND_MODEL
    token_limit = MODEL_TOKEN_LIMITS[model]

    # 为系统提示和模型回复预留空间
    available_tokens = token_limit - 2000

    # 估算查询的tokens
    query_tokens = estimate_tokens(args.query)
    total_tokens = query_tokens + 500  # 添加环境上下文的token估算

    # 读取文件内容（如果指定了-filename）
    file_contents = []

    if args.filename:
        for filename in args.filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                file_tokens = estimate_tokens(content)
                total_tokens += file_tokens
                file_contents.append((filename, content))
                print(f"包含文件内容: {filename} (预估 {file_tokens} tokens)")
            except Exception as e:
                print(f"读取文件 '{filename}' 出错: {str(e)}")
                sys.exit(1)
      
        # 在读取所有文件后，检查token总量
        if total_tokens > 6000:
            print(f"警告: 预估token消耗({total_tokens})可能过大，这可能会导致较高的API调用成本。")
            confirm = input("是否继续操作？(y/N): ")
            if confirm.lower() != 'y':
                print("操作已取消")
                sys.exit(0)
      
        # 检查是否已超出token限制
        if total_tokens > available_tokens:
            print(f"错误: 文件内容太大，预估超过{total_tokens}个tokens")
            print(f"超出了{model}模型的限制({available_tokens} tokens)")
            print("请减少文件数量或使用更小的文件")
            sys.exit(1)

    # 生成bash命令或脚本
    print("正在处理请求...")
    success, result = generate_bash_command(
        args.query, 
        context, 
        is_script=is_script_mode,
        file_contents=file_contents if file_contents else None
    )

    if success:
        if is_script_mode:
            # 生成脚本模式
            script_path = create_script_file(result, args.query)
            append_to_history(
                args.query, 
                result, 
                "script", 
                script_path, 
                args.filename if args.filename else None
            )
            print(f"\n脚本已创建: {script_path}")
            print("您可以使用以下命令运行脚本:")
            print(f"\033[92m{script_path}\033[0m")
        else:
            # 生成单行命令模式 - 仅输出命令结果
            append_to_history(
                args.query, 
                result, 
                "command", 
                None, 
                args.filename if args.filename else None
            )
            print(f"\033[92m{result}\033[0m")  # 绿色输出命令
    else:
        print(f"错误: {result}")


if __name__ == "__main__":
    main()
