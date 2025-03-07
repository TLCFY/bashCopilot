
# Bash-Copilot

Bash-Copilot 是一个基于AI的纯命令行工具，可将自然语言转换为bash命令或脚本。支持生成单行命令和完整的shell脚本，并且能够根据指定文件内容提供上下文相关的命令生成。

## 功能特点

- 🚀 将自然语言查询转换为可执行的bash命令
- 📝 生成完整的shell脚本，包含错误处理和注释
- 📄 支持读取本地文件作为上下文
- 📊 自动估算token使用量，防止超出模型限制
- 📝 自动记录历史查询和生成结果
- 🎨 彩色输出显示生成的命令和脚本

## 环境要求

- Python 3.6+
- Ubuntu 20.04 或类似的Linux系统
- requests库
- 需要API密钥:
  - 硅基流动API密钥 (用于生成单行命令)
  - OpenRouter API密钥 (用于生成脚本)

## 安装

1. 克隆仓库:

```bash
git clone https://github.com/yourusername/bash-copilot.git
cd bash-copilot
```

2. 安装依赖:

```bash
pip install requests
```

3. 配置API密钥:

```bash
# 创建并编辑硅基流动API密钥文件
echo "your_siliconflow_api_key" > api_key.txt

# 创建并编辑OpenRouter API密钥文件
echo "your_openrouter_api_key" > openrouter_key.txt
```

## 使用方法

### 基本用法

生成单行命令:
```bash
python bashCopilot.py "查找当前目录下最大的5个文件"
```

生成完整脚本:
```bash
python bashCopilot.py -script "备份home目录下的所有.conf文件"
```

### 使用文件内容作为上下文

```bash
python bashCopilot.py -filename config.json data.log "分析这些文件"
```

### 帮助信息

```bash
python bashCopilot.py -help
```

## 项目结构

```
.
├── bashCopilot.py      # 主程序文件
├── api_key.txt         # 硅基流动API密钥配置
├── openrouter_key.txt  # OpenRouter API密钥配置
└── bcopilot_history.log # 历史记录文件
```

## 模型说明

- 单行命令生成: 使用 DeepSeek-V3 (硅基流动)
- 脚本生成: 使用 Claude 3.7 Sonnet (OpenRouter)

## 当前功能限制

- `-filename` 参数目前只能与 `-script` 参数一起使用，使用时请先指定 `-script` 参数
- 仅支持读取文本文件，其他格式的文件可能无法处理
- 读取文件时，文件内容会被转换为字符串，可能会导致格式丢失
- 文件内容的token数量有限制，过大的文件可能无法处理
- 仅支持Linux/Unix环境下的bash命令生成
- 计划未来打包至pip安装
- 计划分离API密钥和相应的模型请求格式

## 贡献指南

1. Fork 该仓库
2. 创建新的特性分支
3. 提交您的更改
4. 推送到分支
5. 创建 Pull Request

## 注意事项

- 请确保您的API密钥安全，不要将其公开
- 本项目仅供学习和研究使用，请遵守相关法律法规
- 对于生成的命令和脚本，请在安全的环境中测试，确保其安全性和有效性

## 许可证

[MIT](./LICENSE)

## 作者

[TLCFY](https://github.com/TLCFY)

## 致谢

- 硅基流动API
- OpenRouter
- DeepSeek AI
- Anthropic
