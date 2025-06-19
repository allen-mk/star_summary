# GitHub Star Summary - 项目使用指南

## 🚀 快速开始

### 环境要求
- Python 3.8 或更高版本
- Git

### 1. 虚拟环境设置（推荐）

#### 自动设置（推荐）
```bash
# Unix/Linux/macOS
./setup.sh

# Windows
setup.bat
```

#### 手动设置
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Unix/Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -e .[dev,ai]
```

### 2. 配置环境变量

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的配置：
```bash
# 必需：GitHub Personal Access Token
GITHUB_TOKEN=your_github_token_here

# 可选：OpenAI API Key（用于AI分类）
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 获取 GitHub Token

1. 访问 [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 选择以下权限：
   - `read:user` - 读取用户信息
   - `public_repo` - 访问公共仓库
4. 复制生成的 token 到 `.env` 文件

### 4. 运行工具

```bash
# 激活虚拟环境（如果未激活）
source activate.sh  # Unix/Linux/macOS
# 或
activate.bat        # Windows

# 生成 README.md
star-summary generate

# 查看帮助
star-summary --help
```

## 📝 配置说明

### 输出文件配置

项目支持灵活的输出文件配置，在 `config.yaml` 中：

```yaml
output:
  format: "markdown"  # 输出格式: markdown, json, both
  base_dir: "output"  # 输出基础目录
  
  # Markdown 输出配置
  markdown:
    filename: "README.md"  # 输出文件名
    template: "templates/main.md"  # 模板文件路径
    include_toc: true  # 是否包含目录
    
  # 文件路径配置（支持多种输出路径）
  paths:
    main_readme: "README.md"        # 项目根目录的主README
    docs_readme: "docs/README.md"   # 文档目录的README
    categories_dir: "output/categories"  # 分类详情目录
```

### AI分类配置

```yaml
classification:
  method: "hybrid"  # rules, ai, hybrid

ai_classification:
  enabled: true
  model: "gpt-3.5-turbo"  # 或 "gpt-4"
  always_use: false  # 仅在规则分类失败时使用AI
  fallback_to_rules: true
```

## 🛠️ 高级用法

### 命令行选项

```bash
# 生成不同格式的输出
star-summary generate --format markdown
star-summary generate --format json
star-summary generate --format both

# 使用自定义配置文件
star-summary generate --config my-config.yaml

# 输出到指定目录
star-summary generate --output /path/to/output

# 禁用缓存
star-summary generate --no-cache

# 详细输出
star-summary generate --verbose

# 预览模式（不实际生成文件）
star-summary generate --dry-run
```

### 自定义输出路径

您可以通过命令行或配置文件指定不同的输出文件：

```bash
# 生成到项目根目录的 README.md
star-summary generate --output-path README.md

# 生成到文档目录
star-summary generate --output-path docs/README.md

# 生成到自定义路径
star-summary generate --output-path /path/to/my-stars.md
```

## 🔧 开发指南

### 目录结构

```
src/
├── config/           # 配置管理模块
├── github/           # GitHub API 集成
├── classifier/       # 项目分类器
├── generator/        # 文档生成器
└── cli/              # 命令行接口

templates/            # Markdown 模板
output/              # 输出目录
venv/                # 虚拟环境（自动创建）
```

### 虚拟环境管理

```bash
# 激活虚拟环境
source activate.sh    # Unix/Linux/macOS
activate.bat          # Windows

# 退出虚拟环境
deactivate

# 重新设置环境（如果出现问题）
./setup.sh           # Unix/Linux/macOS
setup.bat            # Windows
```

### 依赖管理

```bash
# 安装新依赖
pip install package_name

# 更新 requirements.txt
pip freeze > requirements.txt

# 安装所有依赖（包括开发和AI功能）
pip install -e .[dev,ai,all]
```

## 🐛 常见问题

### 1. 虚拟环境相关

**问题**：找不到 `star-summary` 命令
**解决**：确保已激活虚拟环境并安装了项目
```bash
source activate.sh
pip install -e .
```

**问题**：依赖冲突
**解决**：重新创建虚拟环境
```bash
rm -rf venv
./setup.sh
```

### 2. GitHub API 相关

**问题**：API 限制错误
**解决**：检查 GitHub Token 是否正确设置，或等待限制重置

**问题**：无法获取星标项目
**解决**：确保 Token 有正确的权限（read:user, public_repo）

### 3. 输出文件相关

**问题**：生成的文件路径不对
**解决**：检查 `config.yaml` 中的输出配置，或使用 `--output-path` 指定路径

## 📚 更多资源

- [GitHub API 文档](https://docs.github.com/en/rest)
- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)
- [项目 GitHub 仓库](https://github.com/AllenHD/star-summary)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
