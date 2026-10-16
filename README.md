# star-summary

自动获取你的 GitHub 星标，用模型归到一个类别，生成 Markdown 目录。

## 安装

```bash
pip install -e .
```

## 配置

按 [`.env.example`](.env.example) 在 GitHub 生成个人访问令牌，复制为 `.env` 后填入：

```bash
export GITHUB_TOKEN=your_token_here
export STAR_SUMMARY_BASE_URL=https://api.openai.com/v1
export STAR_SUMMARY_API_KEY=your_model_api_key
export STAR_SUMMARY_MODEL=gpt-4o-mini
```

地址、密钥和模型名都从这三项环境变量读取，`config.yaml` 里只写变量名。OpenAI 官方、Anthropic 的 OpenAI 兼容端点（`https://api.anthropic.com/v1`）和常见中转都走 Chat Completions。

`output.description_language` 是简介语言代号，例如 `zh-cn`、`en`。留空时目录用 GitHub 原描述。设了代号后，目录里的简介换成该语言的一句介绍，JSON 仍保留原描述，并多一个 `summary`。

`output.format` 默认 `markdown`，只生成目录。设为 `both` 时同时写 JSON，设为 `json` 时只写 JSON。分类不满意时，改 `classify.yaml` 里的偏好或硬性规则，再重新运行。生成的目录会被整份覆盖。

## 使用

```bash
# 默认只生成目录，写到 output/
star-summary generate

# 验证 Token
star-summary validate

# 初始化配置文件
star-summary init
```

## 分类

类别、偏好和硬性规则在 [`classify.yaml`](classify.yaml)。每个星标只进一个类别。模型只看仓库名、描述、语言和 topics。

给 agent 用的步骤在 [`skills/star-summary/SKILL.md`](skills/star-summary/SKILL.md)。那条路径用 agent 自己的模型，不再要 `STAR_SUMMARY_API_KEY`。

## 开发

```bash
pip install -e .[dev]
pytest
```

## 许可

MIT
