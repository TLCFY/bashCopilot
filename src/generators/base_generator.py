#!/usr/bin/env python3
"""
Base generator 模块 - 基础命令生成功能
"""

import json
import requests
from typing import Dict, Tuple, List, Optional

from config.prompts import (
    SCRIPT_PROMPT_TEMPLATE,
    COMMAND_PROMPT_TEMPLATE,
    FILE_CONTENT_PROMPT,
    SCRIPT_FILE_SUFFIX,
    COMMAND_FILE_SUFFIX
)
from src.config.model_manager import ModelManager

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
    # 获取配置
    model_manager = ModelManager()
    
    if is_script:
        # 脚本生成
        provider_config = model_manager.get_script_provider()
        timeout = 120
        print(f"正在使用 {provider_config['model']} 模型生成脚本，可能需要1-2分钟...")
    else:
        # 命令生成  
        provider_config = model_manager.get_command_provider()
        timeout = 30
    
    # 获取API密钥
    api_key = model_manager.get_api_key(provider_config["key_file"])
    if not api_key:
        return False, f"未找到API密钥，请检查 {provider_config['key_file']}"

    # 构建提示词
    if is_script:
        # 使用脚本生成提示词模板
        prompt_text = SCRIPT_PROMPT_TEMPLATE.format(
            query=query,
            current_directory=context['current_directory'],
            username=context['username'],
            hostname=context['hostname'],
            ubuntu_version=context['ubuntu_version']
        )
        
        # 添加文件内容（如果有）
        if file_contents:
            prompt_text += "\n相关文件内容:\n"
            for filename, content in file_contents:
                prompt_text += FILE_CONTENT_PROMPT.format(
                    filename=filename,
                    content=content
                )
            prompt_text += SCRIPT_FILE_SUFFIX
    else:
        # 使用命令生成提示词模板
        prompt_text = COMMAND_PROMPT_TEMPLATE.format(
            query=query,
            current_directory=context['current_directory'],
            username=context['username'],
            hostname=context['hostname'],
            ubuntu_version=context['ubuntu_version']
        )
        
        # 添加文件内容（如果有）
        if file_contents:
            prompt_text += "\n相关文件内容:\n"
            for filename, content in file_contents:
                prompt_text += FILE_CONTENT_PROMPT.format(
                    filename=filename,
                    content=content
                )
            prompt_text += COMMAND_FILE_SUFFIX

    try:
        # 处理特殊提供商: OpenRouter
        if "openrouter" in provider_config["url"]:
            # OpenRouter请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://bash-copilot.local",
                "X-Title": "Bash-Copilot"
            }
            
            # OpenRouter使用Claude格式
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
            
            payload = {
                "model": provider_config["model"],
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 4000
            }
            
        else:
            # 标准OpenAI兼容格式
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            messages = [{"role": "user", "content": prompt_text}]
            
            payload = {
                "model": provider_config["model"],
                "messages": messages,
                "temperature": 0.1 if not is_script else 0.2,
                "max_tokens": 200 if not is_script else 4000
            }
        
        # 发送请求
        response = requests.post(
            url=provider_config["url"],
            headers=headers,
            json=payload,
            timeout=timeout
        )
    
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
