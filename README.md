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
git clone https://github.com/TLCFY/bashCopilot.git
cd bashCopilot
```

2. 创建并激活虚拟环境 (可选):

```bash
python -m venv bashCopilot-env
source bashCopilot-env/bin/activate
```

3. 安装依赖:

```bash
pip install requests
```

4. 配置API密钥:

```bash
# 创建并编辑硅基流动API密钥文件
echo "your_siliconflow_api_key" > config/api_key.txt

# 创建并编辑OpenRouter API密钥文件
echo "your_openrouter_api_key" > config/openrouter_key.txt
```

## 使用方法

### 使用命令行入口

```bash
# 生成单行命令
./src/bcopilot.py "查找当前目录下最大的5个文件"

# 生成完整脚本
./src/bcopilot.py -script "备份home目录下的所有.conf文件"

# 使用文件内容作为上下文
./src/bcopilot.py -filename config.json data.log "分析这些文件"

# 显示帮助信息
./src/bcopilot.py -help
```

### 直接使用主模块

```bash
# 生成单行命令
python src/main.py "查找当前目录下最大的5个文件"

# 生成完整脚本
python src/main.py -script "备份home目录下的所有.conf文件"
```

## 项目结构

```
.
├── config/                  # 配置目录
│   ├── api/                 # API相关配置
│   │   └── endpoints.py     # API端点配置
│   ├── constants.py         # 常量定义
│   ├── prompts.py           # 提示词模板
├── docs/                    # 文档目录
├── logs/                    # 日志目录
├── src/                     # 源代码目录
│   ├── cli/                 # 命令行接口
│   │   └── parser.py        # 命令行参数解析
│   ├── generators/          # 生成器模块
│   │   ├── base_generator.py     # 基础生成器
│   │   ├── command_generator.py  # 命令生成器
│   │   └── script_generator.py   # 脚本生成器
│   ├── log/                 # 日志模块
│   │   └── history.py       # 历史记录功能
│   ├── utils/               # 工具函数
│   │   ├── api_key.py       # API密钥处理
│   │   ├── context.py       # 上下文处理
│   │   ├── file_utils.py    # 文件处理
│   │   └── token_utils.py   # Token估算
│   ├── bcopilot.py          # 命令行入口脚本
│   ├── main.py              # 主程序入口
│   └── bashCopilot.py       # 旧版主程序
├── tests/                   # 测试目录
└── bashCopilot-env/         # 虚拟环境目录
```

## 模型说明

- 单行命令生成: 使用 DeepSeek-V3 (硅基流动)
- 脚本生成: 使用 Claude 3.7 Sonnet (OpenRouter)

## 开发说明

项目正在进行模块化重构，将功能拆分到不同模块以提高代码可维护性：

- 命令行解析模块 (cli/parser.py) 处理参数解析
- 生成器模块 (generators/) 负责生成命令和脚本
- 日志模块 (log/) 管理历史记录
- 工具模块 (utils/) 提供各种辅助功能

## 功能限制

- 读取文件时，文件内容会被转换为字符串，可能会导致格式丢失
- 文件内容的token数量有限制，过大的文件可能无法处理
- 仅支持Linux/Unix环境下的bash命令生成
- 计划未来打包至pip安装
- 计划支持更多模型配置选项

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
