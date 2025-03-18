# 添加模型指南

Bash-Copilot 支持多种大语言模型(LLM)服务商，您可以轻松配置使用自己喜欢的模型。下面是完整的配置指南。

## 查看当前配置

查看当前使用的模型配置：

```bash
bcopilot config show
```

输出示例：

```
当前配置:
- 命令生成: siliconflow (Pro/deepseek-ai/DeepSeek-V3)
- 脚本生成: openrouter (anthropic/claude-3.7-sonnet)
```

## 切换模型

切换到其他已配置的模型服务商：

```bash
# 切换命令生成模型
bcopilot config set command.provider openai

# 切换脚本生成模型  
bcopilot config set script.provider azure
```

## 添加新模型 (交互式)

最简单的方式是使用交互式命令：

```bash
bcopilot config add-provider
```

按照提示输入:
- 提供商名称（如 openai, azure, baidu 等）
- 类型（命令生成、脚本生成或两者）
- API端点URL
- 模型名称
- API密钥（可以直接输入或从文件加载）

## 添加新模型 (手动配置)

您也可以直接编辑配置文件：

1. 打开配置文件 `config/models.yaml`
2. 添加新的提供商配置：

```yaml
# 在 command.models 或 script.models 下添加
your_provider_name:
  url: "https://your-api-endpoint.com/..."
  model: "your-model-name"
  token_limit: 128000  # 模型的最大token限制
  key_file: "config/api/your_provider_key.txt"
```

3. 创建API密钥文件:

```bash
# 创建密钥文件夹（如果不存在）
mkdir -p config/api

# 保存您的API密钥到文件
echo "YOUR_API_KEY" > config/api/your_provider_key.txt
```

4. 切换到新添加的模型:

```bash
bcopilot config set command.provider your_provider_name
# 或
bcopilot config set script.provider your_provider_name
```

## 常见模型配置示例

### OpenAI

```yaml
openai:
  url: "https://api.openai.com/v1/chat/completions"
  model: "gpt-4o"
  token_limit: 128000
  key_file: "config/api/openai_key.txt"
```

### Azure OpenAI

```yaml
azure:
  url: "https://<your-endpoint>.openai.azure.com/openai/deployments/<deployment-name>/chat/completions?api-version=2023-05-15"
  model: "gpt-4"
  token_limit: 128000
  key_file: "config/api/azure_key.txt"
```

### 百度文心

```yaml
baidu:
  url: "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"
  model: "ernie-4.0"
  token_limit: 32000
  key_file: "config/api/baidu_key.txt"
```

## 注意事项

- 不同服务商的请求格式可能略有不同，Bash-Copilot 会尝试自动适配常见的服务商格式
- 确保API密钥文件权限安全，建议使用 `chmod 600` 设置密钥文件权限
- 某些服务商可能需要额外的认证参数，可在高级配置中设置
