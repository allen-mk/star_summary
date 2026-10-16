---
name: star-summary
description: 把当前用户的 GitHub 星标做成按类别阅读的目录，并写出同一份分类数据。在用户要整理星标、重新归属，或修改分类偏好和硬性规则时使用。
---

# 星标目录

用你自己的模型做归属。不要为了归属去调用需要模型 API key 的命令。拉取星标仍使用环境变量 `GITHUB_TOKEN`。

## 分类说明

读取项目里的 `classify.yaml`。文件不存在时，使用下面的默认类别，偏好和硬性规则为空：

- 人工智能：模型、智能体、机器学习和提示词相关的星标。按它是干什么的判断，不按实现语言。
- 编程工具：编辑器、构建、调试、命令行，以及日常写代码会用到的工具。
- Web 开发：浏览器里的应用、前后端框架、网站和 HTTP 接口。
- 客户端与界面：桌面应用、移动应用和界面组件。
- 系统与基础设施：操作系统、运行时、容器、部署和云。
- 数据与存储：数据库、数据管道和分析。
- 安全：认证、加密、漏洞和安全工具。
- 学习与资料：教程、书籍、手册和资料合集。
- 未归类：没有更合适的类别时放这里。

文件存在时，以文件里的类别、偏好和硬性规则为准。未归类必须保留。

## 拉取星标

`GITHUB_TOKEN` 不存在就停下来，说明需要这个环境变量。不要改用本机 `gh` 的登录态。

用这个 token 请求 `https://api.github.com/user/starred?per_page=100`，按 `Link` 头翻页，直到没有下一页。每个星标只保留仓库名、描述、语言、topics、地址、星数。

## 归属

只根据仓库名、描述、语言、topics 判断。不要读 README 或源码。

每个星标恰好一个类别。类别名必须来自分类说明。没有合适类别时使用未归类。不要新造类别名。

偏好是口味。硬性规则是必须遵守的句子。

## 生成物

全部星标都有归属之后再写文件。缺任何一个星标的归属时不要动已有文件。

`output.format` 为 `markdown` 时只写目录，为 `both` 时目录和分类数据都写，为 `json` 时只写分类数据。默认是 `markdown`。

目录是 Markdown，默认 `output/README.md`。类别顺序与分类说明一致。没有星标的类别不出现。同一类别里按星数从高到低。

读取 `config.yaml` 的 `output.description_language`。它是语言代号，例如 `zh-cn`、`en`，大小写不敏感。留空或没有这个字段时，目录简介用 GitHub 原描述。设了代号后，用仓库名、描述、语言和 topics 为每个星标写一句该语言的简介，目录用这句替换原描述；没有描述时也要写。不要翻译仓库名。

分类数据是 JSON，默认 `output/starred_repos.json`。`metadata` 包含 `generated_at` 和 `total_repos`。`repositories` 的每条包含 `full_name`、`html_url`、`description`、`language`、`topics`、`stargazers_count` 和恰好一个 `category`。`description` 始终是 GitHub 原描述。设了简介语言时再加 `summary`，内容与目录里的简介相同。
