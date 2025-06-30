# 🌟 GitHub 星标项目分类整理工具

> 自动抓取并分类整理你的 GitHub 星标项目，生成美观的 Markdown 文档

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/AllenHD/star-summary.svg)](https://github.com/AllenHD/star-summary/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/AllenHD/star-summary.svg)](https://github.com/AllenHD/star-summary/issues)

## ✨ 特性

- 🔄 **自动获取** - 自动抓取 GitHub 星标项目
- 🏷️ **智能分类** - 多维度分类（语言、用途、技术栈）
- 📝 **文档生成** - 生成结构化 Markdown 文档
- 🎨 **自定义模板** - 支持自定义模板和分类规则
- ⚡ **本地缓存** - 提高运行效率，避免重复请求
- 🤖 **自动更新** - GitHub Actions 自动更新
- 📊 **JSON API** - 提供标准化的 JSON 数据接口
- 🎯 **CLI工具** - 完整的命令行界面
- 🐳 **Docker支持** - 容器化部署

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/AllenHD/star-summary.git
cd star-summary

# 安装依赖
pip install -r requirements.txt

# 或者直接安装
pip install -e .
```

### 配置

1. 获取 GitHub Personal Access Token：
   - 访问 [GitHub Settings → Developer settings → Personal access tokens](https://github.com/settings/tokens)
   - 创建新token，勾选 `public_repo` 权限

2. 设置环境变量：

```bash
# 方法1：设置环境变量
export GITHUB_TOKEN=your_token_here

# 方法2：创建 .env 文件
echo "GITHUB_TOKEN=your_token_here" > .env
```

### 使用

```bash
# 生成 Markdown 文档
star-summary generate

# 生成 JSON 数据
star-summary generate --format json

# 同时生成 Markdown 和 JSON
star-summary generate --format both

# 验证 Token
star-summary validate

# 查看系统状态
star-summary status
```

## 📚 文档

- [📦 安装说明](INSTALL.md) - 详细的安装和配置指南
- [📖 使用说明](USAGE.md) - 完整的使用教程和API参考
- [⚙️ 配置文件](config.yaml) - 配置选项说明
- [🎨 模板系统](templates/) - 自定义模板开发

## 🛠️ 命令行工具

### 主命令

```bash
# 生成文档
star-summary generate [OPTIONS]

# 系统状态检查
star-summary status

# 验证GitHub Token
star-summary validate --token TOKEN
```

### 工具命令

```bash
# 列出星标项目
star-summary-tools list-repos --limit 20 --sort-by stars

# 测试项目分类
star-summary-tools classify --repo-name "microsoft/vscode"

# 模板管理
star-summary-tools template

# 缓存管理
star-summary-tools cache --size
```

## 🔧 配置

项目使用 `config.yaml` 进行配置：

```yaml
# GitHub 配置
github:
  token_env: "GITHUB_TOKEN"
  timeout: 30
  per_page: 100

# 分类配置
classification:
  method: "rules"  # rules, ai, hybrid

# 输出配置
output:
  format: "markdown"  # markdown, json, both
  base_dir: "output"

# 缓存配置
cache:
  enabled: true
  ttl_hours: 24
```

## 🎯 分类系统

### 技术栈分类
- 🐍 Python
- 🟨 JavaScript / TypeScript
- ☕ Java
- 🔵 C# / C++
- 🦀 Rust
- 🔷 Go

### 用途分类
- 🤖 AI/机器学习
- 🎨 Web前端
- ⚙️ Web后端
- 📱 移动开发
- 🎮 游戏开发
- 🔧 开发工具

### 自定义分类

可以通过修改 `config.yaml` 添加自定义分类规则：

```yaml
categories:
  tech_stack:
    my-category:
      - "keyword1"
      - "keyword2"
```

## 🚀 部署

### Docker 部署

```bash
# 构建镜像
docker build -t star-summary .

# 运行容器
docker run -e GITHUB_TOKEN=your_token_here star-summary
```

### GitHub Actions

项目包含预配置的 GitHub Actions 工作流，可以：
- 每天自动更新星标项目
- 手动触发更新
- 自动部署到 GitHub Pages

### 本地定时任务

```bash
# 添加到 crontab
0 2 * * * cd /path/to/star-summary && star-summary generate
```

## 📊 API 数据格式

生成的 JSON API 数据结构：

```json
{
  "metadata": {
    "generated_at": "2023-01-01T00:00:00",
    "version": "1.0.0",
    "total_repos": 100,
    "categories": ["ai-ml", "web-frontend", ...],
    "languages": ["Python", "JavaScript", ...],
    "stats": {...}
  },
  "repositories": [
    {
      "id": 123456,
      "name": "repo-name",
      "full_name": "owner/repo-name",
      "description": "Repository description",
      "html_url": "https://github.com/owner/repo-name",
      "language": "Python",
      "stargazers_count": 1000,
      "categories": ["ai-ml", "python"],
      ...
    }
  ]
}
```

## 🤝 贡献

欢迎贡献代码！请阅读 [贡献指南](CONTRIBUTING.md) 了解详情。

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

## 📄 许可证

此项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [PyGithub](https://github.com/PyGithub/PyGithub) - GitHub API 客户端
- [Click](https://github.com/pallets/click) - 命令行界面框架
- [Jinja2](https://github.com/pallets/jinja) - 模板引擎
- [colorama](https://github.com/tartley/colorama) - 终端颜色支持

## 📞 支持

如果你觉得这个项目有用，请给个 ⭐ Star！

- 📧 Email: your-email@example.com
- 🐛 Bug报告: [GitHub Issues](https://github.com/AllenHD/star-summary/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/AllenHD/star-summary/discussions)

---

**Made with ❤️ by [AllenHD](https://github.com/AllenHD)**
