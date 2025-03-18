#!/usr/bin/env python3
"""
配置管理命令 - 处理模型配置
"""

import os
import sys
from src.config.model_manager import ModelManager

def handle_config_command(args):
    """处理配置相关命令"""
    manager = ModelManager()
    
    if args.action == "show":
        # 显示当前配置
        command_provider = manager.get_command_provider()
        script_provider = manager.get_script_provider()
        
        print("当前配置:")
        print(f"- 命令生成: {manager.config['command']['provider']} ({command_provider['model']})")
        print(f"- 脚本生成: {manager.config['script']['provider']} ({script_provider['model']})")
        
    elif args.action == "set":
        # 设置提供商
        try:
            type_name, provider_name = args.value.split(".", 1)
            manager.set_provider(type_name, provider_name)
            print(f"已将 {type_name} 提供商设置为 {provider_name}")
        except ValueError as e:
            print(f"错误: {str(e)}")
            print("格式应为: 'command.provider_name' 或 'script.provider_name'")
            
    elif args.action == "add-provider":
        # 交互式添加提供商
        provider_name = input("提供商名称: ")
        
        while True:
            type_name = input("提供商类型 [command/script/both]: ").lower()
            if type_name in ["command", "script", "both"]:
                break
            print("无效的类型，请输入 'command', 'script' 或 'both'")
            
        url = input("API端点URL: ")
        model = input("模型名称: ")
        
        try:
            token_limit = int(input("令牌限制: "))
        except:
            token_limit = 100000
            print(f"使用默认令牌限制: {token_limit}")
            
        key_file = input(f"API密钥文件路径 [config/api/{provider_name}_key.txt]: ")
        if not key_file:
            key_file = f"config/api/{provider_name}_key.txt"
            
        # 创建密钥文件
        full_key_path = os.path.join(manager.root_dir, key_file)
        os.makedirs(os.path.dirname(full_key_path), exist_ok=True)
        
        if not os.path.exists(full_key_path):
            api_key = input("API密钥: ")
            with open(full_key_path, "w") as f:
                f.write(api_key)
            print(f"已保存API密钥到 {key_file}")
            
        # 添加提供商
        try:
            manager.add_provider(type_name, provider_name, url, model, token_limit, key_file)
            print(f"✓ 提供商 '{provider_name}' 添加成功！")
        except Exception as e:
            print(f"添加提供商失败: {str(e)}")
            
    elif args.action == "list-providers":
        # 列出所有提供商
        print("命令生成提供商:")
        for provider in manager.config["command"]["models"]:
            config = manager.config["command"]["models"][provider]
            current = " (当前)" if provider == manager.config["command"]["provider"] else ""
            print(f"- {provider}: {config['model']}{current}")
            
        print("\n脚本生成提供商:")
        for provider in manager.config["script"]["models"]:
            config = manager.config["script"]["models"][provider]
            current = " (当前)" if provider == manager.config["script"]["provider"] else ""
            print(f"- {provider}: {config['model']}{current}")
