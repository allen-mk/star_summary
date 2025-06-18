感谢补充信息。请再确认以下几点，以便我为你生成最合适的开发文档：
	1.	你希望文档初期输出的格式是一份或多份 Markdown 文件，是否有示例你想模仿的风格或结构？
	2.	你希望自动脚本通过 GitHub API 获取数据，是否已经有 GitHub Token？
	3.	前端展示部分：你更倾向于使用现成框架（如 React 或 Vue）还是轻量级静态网页？
	4.	你计划将这个项目部署到哪里？（例如 GitHub Pages、Vercel、Netlify 等）

请确认这些细节后，我将为你生成完整的开发文档。

Research is not currently supported in temporary chats.

由于你当前处于临时对话中，我无法执行完整的研究任务，但我可以为你提供初步的项目开发文档草稿（Markdown 格式），供你作为项目 README 或开发计划使用。你可以在此基础上继续完善：

⸻

⭐ GitHub 星标项目分类整理工具

一个用于自动抓取并分类整理本人 GitHub 星标项目的 Python 工具，输出结构化的 Markdown 文档，并支持未来扩展为前端展示界面。

⸻

📌 项目目标
	•	自动抓取 GitHub 账户的所有星标项目。
	•	按照 技术栈 和 项目用途 分类。
	•	输出结构清晰、可跳转的 Markdown 文档。
	•	后期支持部署前端页面，支持搜索、筛选与分类展示。

⸻

🧩 项目功能需求

核心功能
	1.	获取 GitHub 星标项目
	•	使用 GitHub API 获取用户已星标的项目列表。
	•	支持通过 GitHub Token 提高 API 访问限制。
	2.	项目分类
	•	按照：
	•	技术栈（Python、JavaScript、Rust 等）
	•	项目用途（Web 开发、数据分析、机器学习、工具类等）
	•	支持多种分类方式：
		- 基于规则的传统分类（语言、topics、关键词匹配）
		- AI大模型智能分类（可选，支持OpenAI GPT模型）
		- 混合分类模式（规则+AI增强，推荐方式）
	3.	Markdown 文档生成
	•	输出目录结构清晰的 Markdown 文件。
	•	每个项目附带 GitHub 链接、描述、语言、标签等。
	4.	自动更新脚本
	•	支持通过定时任务（cron）或命令行手动运行。
	•	每次运行自动更新 Markdown 文件内容。

⸻

🌐 后期扩展功能
	5.	前端展示界面
	•	使用轻量级前端框架（建议 React + Tailwind 或 Vue）展示分类结果。
	•	实现：
	•	标签过滤
	•	项目搜索
	•	分类浏览
	6.	部署选项
	•	GitHub Pages
	•	Netlify 或 Vercel 静态托管

⸻

🛠️ 任务拆解

模块	任务内容
GitHub 数据获取	接入 API，拉取用户星标项目，支持分页处理
数据预处理	提取项目关键词、语言、话题，清洗分类标签
分类逻辑	基于规则（如语言字段 + topic 标签）实现自动分类，支持AI大模型增强分类
Markdown 输出	构建目录结构、生成分层文档、嵌入跳转链接
自动化脚本	命令行脚本 + 定时运行逻辑
前端原型（阶段二）	使用 React/Vue 渲染分类，实现基本交互与搜索


⸻

🔧 技术栈建议
	•	后端脚本：Python 3.x
	•	requests / httpx（API 请求）
	•	jinja2（模板生成 Markdown 可选）
	•	PyYAML / JSON（配置）
	•	openai（可选，AI分类功能）
	•	前端界面（可选扩展）：
	•	React / Vue + TailwindCSS
	•	部署：
	•	GitHub Pages（前端）+ GitHub Actions（自动更新）

⸻

## 🤖 AI分类功能说明

### 分类模式选择
- **规则分类** (`rules`) - 基于预定义规则的传统分类方式
- **AI分类** (`ai`) - 使用OpenAI GPT模型进行智能分类
- **混合分类** (`hybrid`) - 结合规则和AI的增强分类模式（推荐）

### AI分类特性
- **智能识别**：基于项目名称、描述、语言、topics等信息进行分析
- **多维分类**：支持技术栈、用途、编程语言等多个维度的分类
- **置信度评估**：提供分类结果的置信度评分
- **错误恢复**：AI分类失败时自动回退到规则分类
- **成本控制**：可配置仅在规则分类无法准确分类时启用AI

### 配置示例
```yaml
classification:
  method: "hybrid"  # rules, ai, hybrid
  
ai_classification:
  enabled: true
  api_key_env: "OPENAI_API_KEY"
  model: "gpt-3.5-turbo"
  always_use: false
  fallback_to_rules: true
```

