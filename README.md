# GitHub 星标项目分类整理工具

一个强大的 GitHub 星标项目自动分类整理工具，支持智能分类和美观的 Markdown 文档生成。

## 功能特性

- 🌟 **自动获取**：自动抓取 GitHub 账户的所有星标项目
- 🏷️ **智能分类**：支持规则分类、AI大模型分类和混合分类模式
- 📄 **文档生成**：输出结构清晰的 Markdown 文档
- ⚙️ **灵活配置**：支持自定义分类规则和输出格式
- 🔄 **自动更新**：支持定期更新和增量同步
- 🎨 **美观展示**：生成专业的项目展示页面

## 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.8 或更高版本。

### 2. 安装和设置

```bash
# 克隆项目
git clone https://github.com/yourusername/star-summary.git
cd star-summary

# 自动设置虚拟环境（推荐）
./setup.sh  # Linux/macOS
# 或
setup.bat   # Windows

# 手动设置虚拟环境
python -m venv star_summary_env
source star_summary_env/bin/activate  # Linux/macOS
# 或
star_summary_env\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置

复制环境变量模板并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置您的 GitHub Token：

```env
GITHUB_TOKEN=your_github_token_here
```

### 4. 运行

```bash
# 激活虚拟环境（如果未激活）
source star_summary_env/bin/activate

# 运行分类工具
python -m cli.main --username your_github_username
```

## 配置说明

项目配置在 `config.yaml` 文件中，主要配置项包括：

- **github**: GitHub API 相关配置
- **classification**: 分类方法配置
- **output**: 输出格式和路径配置
- **ai_classification**: AI 分类相关配置（可选）

详细配置说明请参考 [docs/USAGE.md](docs/USAGE.md)。

## 分类模式

### 1. 规则分类（rules）
基于项目的编程语言、topics 和描述关键词进行分类。

### 2. AI 分类（ai）
使用大语言模型进行智能分类，需要配置 OpenAI API Key。

### 3. 混合分类（hybrid）
结合规则分类和 AI 分类的优势，提供最佳的分类效果。

## 输出格式

默认输出为 `README.md`，支持自定义文件名和路径：

```yaml
output:
  format: "markdown"
  base_dir: "output"
  markdown:
    filename: "README.md"  # 可自定义
  paths:
    main_readme: "README.md"
    docs_readme: "docs/README.md"
```

## 虚拟环境管理

为避免依赖冲突，项目强烈建议使用虚拟环境：

1. **自动设置**：使用提供的脚本自动创建和配置虚拟环境
2. **手动设置**：按照上述步骤手动创建虚拟环境
3. **环境激活**：每次使用前确保激活虚拟环境

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

*这个文档是由 GitHub 星标项目分类整理工具自动生成的。*
