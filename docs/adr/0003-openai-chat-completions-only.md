# 模型接入只走 OpenAI Chat Completions

OpenAI 官方、Anthropic 官方的 OpenAI 兼容端点（`https://api.anthropic.com/v1/`），以及 OpenRouter、SiliconFlow 和常见中转，都可以用 `base_url` + `api_key` + `model` 调用 Chat Completions。分类只需要一段 JSON 文本。因此不再设 api 类型，也不再为 Anthropic Messages 单写一个客户端。只提供 Messages、不提供 Chat Completions 的端点不在这条接入里。
