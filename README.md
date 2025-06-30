# 🌟 GitHub 星标项目智能分类整理工具

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue.svg)](https://github.com/AllenHD/star-summary/actions)
[![Docker Support](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://docker.com)

> **智能化的GitHub星标项目管理解决方案** - 自动获取、智能分类、生成文档，支持多种输出格式和部署方式

## 🚀 核心特性

### � 智能分类系统
- **📊 多维度分类** - 基于编程语言、技术栈、用途、领域等44个预定义分类
- **🤖 AI增强分类** - 可选的OpenAI GPT模型智能分类（支持GPT-3.5和GPT-4）
- **🔄 混合分类模式** - 规则分类+AI分类，确保准确性和智能性
- **📏 置信度评分** - 每个分类结果包含置信度评分和推理过程

### 🛠️ 强大的CLI工具
- **💻 双命令入口** - `star-summary`主命令 + `star-summary-tools`工具命令
- **📝 多格式输出** - Markdown、JSON、或同时生成两种格式
- **🔍 项目检索** - 支持项目搜索、排序、筛选和详细信息查看
- **⚙️ 系统管理** - 配置验证、缓存管理、模板操作等完整工具集

### 📊 数据接口与集成
- **🔗 标准化JSON API** - 为前端开发提供结构化数据接口
- **📋 完整元数据** - 包含17个标准字段的项目信息
- **📈 统计分析** - 自动生成分类统计、语言分布等分析报告
- **🔌 可扩展性** - 支持自定义字段和数据结构扩展

### ⚡ 高性能与可靠性
- **💾 智能缓存系统** - 可配置的多级缓存，支持TTL和自动清理
- **🚦 速率限制管理** - 自动检测和处理GitHub API限制
- **🔄 错误恢复** - 完善的重试机制和错误处理
- **📊 详细日志** - 多级别日志记录，支持详细调试信息

### 🤖 自动化部署
- **⏰ 定时更新** - GitHub Actions每日自动更新星标项目
- **🚀 一键部署** - 支持GitHub Pages自动部署
- **🐳 容器化支持** - Docker和docker-compose完整配置
- **� 多环境适配** - 开发、测试、生产环境配置分离

## � 快速开始

### 🔧 安装部署

#### 方法1：直接安装
```bash
# 克隆项目
git clone https://github.com/AllenHD/star-summary.git
cd star-summary

# 安装为可执行包
pip install -e .

# 创建配置文件
star-summary init
```

#### 方法2：Docker部署
```bash
# 使用docker-compose
docker-compose up -d

# 或使用Docker直接运行
docker build -t star-summary .
docker run -e GITHUB_TOKEN=your_token star-summary
```

### ⚙️ 配置设置

1. **获取GitHub Token**
   ```bash
   # 访问 https://github.com/settings/tokens
   # 创建Personal Access Token，勾选 'public_repo' 权限
   ```

2. **环境变量配置**
   ```bash
   # 设置GitHub Token
   export GITHUB_TOKEN=your_github_token_here
   
   # 可选：设置OpenAI API Key（启用AI分类）
   export OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **配置文件调整**
   ```yaml
   # config.yaml
   classification:
     method: "hybrid"  # rules, ai, hybrid
   
   output:
     format: "both"    # markdown, json, both
     
   ai_classification:
     enabled: true
     model: "gpt-3.5-turbo"
   ```

### 🎯 基础使用

```bash
# 生成完整分类文档
star-summary generate

# 生成JSON数据接口
star-summary generate --format json

# 同时生成Markdown和JSON
star-summary generate --format both --output docs/

# 系统状态检查
star-summary status

# GitHub Token验证
star-summary validate

# 项目初始化
star-summary init --force
```

## 🛠️ 高级功能

### 📊 项目分析工具

```bash
# 列出星标项目（支持排序和筛选）
star-summary-tools list-repos --limit 50 --sort-by stars --format table

# 测试分类效果
star-summary-tools classify --repo-name "microsoft/vscode" --method hybrid

# 查看分类统计
star-summary-tools classify --method rules
```

### 🎨 模板管理

```bash
# 查看可用模板
star-summary-tools template

# 查看特定模板内容
star-summary-tools template --template-name main.md

# 自定义模板开发（见templates/目录）
```

### 💾 缓存管理

```bash
# 查看缓存状态
star-summary-tools cache

# 查看缓存大小
star-summary-tools cache --size

# 清空缓存
star-summary-tools cache --clear
```

## 🏗️ 核心架构

### � 模块化设计
```
src/
├── config/         # 配置管理系统
├── github_api/     # GitHub API集成层
├── classifier/     # 智能分类引擎
├── generator/      # 文档和API生成器
├── cli/           # 命令行接口
└── utils/         # 通用工具库
```

### 🔄 数据流处理
```
GitHub API → 数据获取 → 智能分类 → 文档生成 → 多格式输出
     ↓           ↓           ↓           ↓
   缓存系统    分类引擎    模板系统    JSON API
```

## 🎯 智能分类体系

### 💻 技术栈分类（16个）
- **前端技术**: React, Vue, Angular, Svelte等
- **后端框架**: Django, Flask, Express, FastAPI等  
- **移动开发**: Flutter, React Native, Swift, Kotlin等
- **数据科学**: TensorFlow, PyTorch, Pandas, Jupyter等
- **DevOps**: Docker, Kubernetes, Terraform, CI/CD等

### 🎨 功能分类（28个）
- **开发工具**: 编辑器、IDE、调试工具、构建工具
- **框架库**: 开发框架、组件库、工具库
- **学习资源**: 教程、文档、示例项目、书籍
- **企业应用**: CRM、ERP、监控、部署平台

### 🔬 领域分类
- **人工智能**: 机器学习、深度学习、自然语言处理
- **区块链**: 加密货币、智能合约、DeFi应用
- **游戏开发**: 游戏引擎、工具、资源
- **安全工具**: 漏洞扫描、渗透测试、加密工具

## 📊 输出格式

### 📝 Markdown文档
- **📋 目录结构** - 自动生成的分类目录
- **📊 统计信息** - 项目统计、语言分布、更新状态
- **🏷️ 项目详情** - 完整的项目信息和分类标签
- **🎨 美化格式** - 表格、徽章、图标等视觉元素

### 📋 JSON API数据
```json
{
  "metadata": {
    "version": "1.0.0",
    "generated_at": "2025-06-30T12:00:00Z",
    "total_repos": 150,
    "total_categories": 12
  },
  "statistics": {
    "by_language": {"Python": 45, "JavaScript": 38},
    "by_category": {"web-development": 25, "ai-ml": 20}
  },
  "repositories": [
    {
      "id": 123456,
      "name": "awesome-project",
      "full_name": "user/awesome-project",
      "description": "项目描述",
      "classification": {
        "categories": ["web-development", "frontend"],
        "method": "hybrid",
        "confidence": 0.95,
        "reasoning": "基于React框架和前端技术栈"
      }
    }
  ]
}
```

## 🤖 自动化与部署

### ⏰ GitHub Actions集成
```yaml
# .github/workflows/update-stars.yml
# ✅ 每日自动更新
# ✅ 手动触发执行  
# ✅ 多格式输出
# ✅ GitHub Pages部署
# ✅ 错误处理和重试
```

### 🐳 Docker容器化
```yaml
# docker-compose.yml
version: '3.8'
services:
  star-summary:
    build: .
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    volumes:
      - ./output:/app/output
    command: star-summary generate --format both
```

### � 部署选项
- **GitHub Pages** - 自动部署静态文档
- **Docker容器** - 本地或云端部署
- **定时任务** - Cron或调度系统集成
- **API服务** - 作为数据API服务部署

## 📚 详细文档

- **[📦 安装指南](INSTALL.md)** - 详细的安装配置说明
- **[📖 使用教程](USAGE.md)** - 完整的功能使用指南  
- **[⚙️ 配置参考](config.yaml)** - 配置文件详细说明
- **[🎨 模板开发](templates/)** - 自定义模板开发文档
- **[🔧 API文档](src/generator/api.py)** - JSON API接口说明

## 🤝 项目信息

### 📊 技术栈
- **核心语言**: Python 3.8+
- **框架库**: Click, Jinja2, PyGithub, PyYAML
- **AI集成**: OpenAI GPT API
- **容器化**: Docker, docker-compose
- **CI/CD**: GitHub Actions

### 📈 项目状态
- **🎯 已完成**: 6个核心模块全部实现
- **✅ 生产就绪**: 完整的错误处理和日志系统
- **🚀 持续集成**: 自动化测试和部署
- **� 文档完善**: 详细的使用和开发文档

### 🔗 相关链接
- **代码仓库**: [GitHub](https://github.com/AllenHD/star-summary)
- **问题反馈**: [Issues](https://github.com/AllenHD/star-summary/issues)
- **更新日志**: [Releases](https://github.com/AllenHD/star-summary/releases)
- **在线演示**: [GitHub Pages](https://allenHD.github.io/star-summary)


## 🔧 快速命令参考

### 📝 常用操作
```bash
# 完整工作流程
star-summary init                    # 初始化配置
star-summary validate               # 验证Token
star-summary generate --format both # 生成文档和数据

# 项目分析
star-summary-tools list-repos --limit 10 --sort-by stars
star-summary-tools classify --repo-name "facebook/react"

# 系统维护
star-summary status                 # 系统状态
star-summary-tools cache --clear   # 清理缓存
```

### ⚙️ 高级配置示例
```yaml
# config.yaml - 生产环境配置
github:
  timeout: 60
  retry_count: 5
  per_page: 100

classification:
  method: "hybrid"  # 使用混合分类模式

ai_classification:
  enabled: true
  model: "gpt-4"    # 使用更强大的模型
  fallback_to_rules: true

output:
  format: "both"
  base_dir: "docs"
  
cache:
  enabled: true
  ttl_hours: 24
  auto_cleanup: true
```

## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 🤝 贡献指南

欢迎提交 Issues 和 Pull Requests！

1. **Fork** 本仓库
2. **创建** 功能分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 更改 (`git commit -m 'Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **开启** Pull Request

## 💡 路线图

- [ ] **Web界面** - 基于React的可视化管理界面
- [ ] **插件系统** - 支持自定义分类插件
- [ ] **多平台支持** - GitLab, Bitbucket等平台集成
- [ ] **团队协作** - 多用户、权限管理
- [ ] **AI增强** - 更智能的项目分析和推荐

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给它一个星标！**

**📧 联系方式**: [GitHub Issues](https://github.com/AllenHD/star-summary/issues)

**🔔 获取更新**: [Watch this repo](https://github.com/AllenHD/star-summary/subscription)


</div>
