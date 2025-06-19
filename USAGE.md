# 使用说明

## 快速开始

### 1. 基础使用

生成你的 GitHub 星标项目分类文档：

```bash
# 生成默认 Markdown 文档
star-summary generate

# 指定输出目录
star-summary generate --output my-docs/

# 生成 JSON 格式
star-summary generate --format json

# 同时生成 Markdown 和 JSON
star-summary generate --format both
```

### 2. 系统检查

```bash
# 检查系统状态
star-summary status

# 验证 GitHub Token
star-summary validate --token your_token_here
```

## 命令详解

### 主命令：`star-summary`

#### `generate` - 生成文档

```bash
star-summary generate [OPTIONS]
```

**选项：**
- `--token TEXT` - GitHub 个人访问令牌
- `--config TEXT` - 配置文件路径（默认：config.yaml）
- `--output TEXT` - 输出目录（默认：output）
- `--format [markdown|json|both]` - 输出格式（默认：markdown）
- `--no-cache` - 禁用缓存
- `--dry-run` - 预览模式，显示将要执行的操作
- `--max-repos INTEGER` - 限制处理的项目数量（用于测试）

**示例：**
```bash
# 基础生成
star-summary generate

# 预览模式
star-summary generate --dry-run

# 限制项目数量（测试用）
star-summary generate --max-repos 50

# 生成到指定目录
star-summary generate --output ~/Documents/my-stars/

# 使用自定义配置
star-summary generate --config my-config.yaml

# 禁用缓存，强制重新获取
star-summary generate --no-cache
```

#### `status` - 系统状态检查

```bash
star-summary status
```

显示：
- 配置文件状态
- GitHub Token 状态
- 缓存状态
- 依赖检查

#### `validate` - 验证 Token

```bash
star-summary validate --token your_token_here
```

验证 GitHub Token 的有效性和权限。

### 工具命令：`star-summary-tools`

#### `list-repos` - 列出星标项目

```bash
star-summary-tools list-repos [OPTIONS]
```

**选项：**
- `--token TEXT` - GitHub Token（必需）
- `--format [table|json|csv]` - 输出格式
- `--limit INTEGER` - 显示项目数量限制
- `--sort-by [stars|forks|updated|name]` - 排序方式

**示例：**
```bash
# 表格形式显示前20个项目，按星标排序
star-summary-tools list-repos --limit 20 --sort-by stars

# JSON 格式输出
star-summary-tools list-repos --format json --limit 10

# CSV 格式输出（可导入Excel）
star-summary-tools list-repos --format csv > my-stars.csv
```

#### `classify` - 测试项目分类

```bash
star-summary-tools classify [OPTIONS]
```

**选项：**
- `--token TEXT` - GitHub Token（必需）
- `--method [rules|ai|hybrid]` - 分类方法
- `--repo-name TEXT` - 指定仓库名称（格式：owner/repo）

**示例：**
```bash
# 分类单个项目
star-summary-tools classify --repo-name "microsoft/vscode"

# 批量分类测试（前10个项目）
star-summary-tools classify

# 使用 AI 分类
star-summary-tools classify --method ai --repo-name "openai/gpt-3"
```

#### `template` - 模板管理

```bash
star-summary-tools template [OPTIONS]
```

**选项：**
- `--template-name TEXT` - 指定模板名称

**示例：**
```bash
# 列出所有模板
star-summary-tools template

# 查看特定模板
star-summary-tools template --template-name main.md
```

#### `cache` - 缓存管理

```bash
star-summary-tools cache [OPTIONS]
```

**选项：**
- `--clear` - 清空缓存
- `--size` - 显示缓存大小

**示例：**
```bash
# 查看缓存状态
star-summary-tools cache

# 显示缓存大小
star-summary-tools cache --size

# 清空缓存
star-summary-tools cache --clear
```

## 配置文件详解

配置文件 `config.yaml` 包含所有可定制的选项：

### GitHub 配置

```yaml
github:
  token_env: "GITHUB_TOKEN"  # Token 环境变量名
  timeout: 30               # 请求超时时间
  per_page: 100            # 每页获取项目数
  rate_limit:
    check_threshold: 100    # 速率限制检查阈值
    wait_on_limit: true    # 遇到限制时是否等待
```

### 分类配置

```yaml
classification:
  method: "rules"  # 分类方法：rules, ai, hybrid

# AI 分类配置（可选）
ai_classification:
  enabled: true
  model: "gpt-3.5-turbo"
  always_use: false
  fallback_to_rules: true
```

### 输出配置

```yaml
output:
  format: "markdown"  # 输出格式
  base_dir: "output"  # 输出目录
  
  markdown:
    filename: "README.md"
    include_toc: true
    
  json:
    filename: "starred-projects.json"
    pretty_print: true
```

### 缓存配置

```yaml
cache:
  enabled: true
  ttl_hours: 24        # 缓存有效期
  cache_dir: ".cache"
  auto_cleanup: true
```

## 高级用法

### 1. 自定义分类规则

编辑 `config.yaml` 中的分类规则：

```yaml
categories:
  tech_stack:
    web-frontend:
      - "react"
      - "vue"
      - "angular"
    ai-ml:
      - "tensorflow"
      - "pytorch"
      - "machine-learning"
```

### 2. 多配置文件

为不同用途创建不同配置：

```bash
# 开发环境配置
star-summary generate --config config-dev.yaml

# 生产环境配置  
star-summary generate --config config-prod.yaml
```

### 3. 定时任务

使用 cron 定时更新文档：

```bash
# 每天凌晨2点更新
0 2 * * * cd /path/to/star-summary && star-summary generate
```

### 4. GitHub Actions 集成

创建 `.github/workflows/update-stars.yml`：

```yaml
name: Update Star Summary
on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -e .
      - name: Generate documentation
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: star-summary generate
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add output/
          git commit -m "Update star summary" || exit 0
          git push
```

## 故障排除

### 常见错误

#### 1. Token 权限不足
```
Error: 403 Forbidden
```
**解决方案**：确保 token 有 `public_repo` 权限

#### 2. 网络超时
```
Error: Request timeout
```
**解决方案**：增加超时时间或检查网络连接

#### 3. 缓存问题
```
Error: Cache corruption
```
**解决方案**：清空缓存
```bash
star-summary-tools cache --clear
```

#### 4. 分类失败
```
Error: Classification failed
```
**解决方案**：检查配置文件中的分类规则

### 调试模式

启用详细日志：

```bash
# 设置日志级别
export LOG_LEVEL=DEBUG
star-summary generate

# 或编辑配置文件
# config.yaml
logging:
  level: "DEBUG"
```

## 性能优化

### 1. 缓存策略
- 启用缓存以避免重复 API 调用
- 定期清理过期缓存

### 2. 网络优化
- 使用代理（如需要）
- 调整超时时间和重试次数

### 3. 批量处理
- 使用 `--max-repos` 测试配置
- 分批处理大量项目

## 扩展功能

### 1. 自定义模板

复制并修改模板文件：

```bash
cp templates/main.md templates/my-template.md
# 编辑 my-template.md
```

### 2. 插件开发

扩展分类器：

```python
# custom_classifier.py
from src.classifier.rules import RuleEngine

class CustomClassifier(RuleEngine):
    def classify(self, repo_data):
        # 自定义分类逻辑
        pass
```

### 3. 导出格式

添加新的导出格式（HTML、PDF等）通过扩展 `DocumentExporter` 类。

## 示例工作流

### 个人使用
```bash
# 1. 生成个人星标文档
star-summary generate

# 2. 查看分类效果
star-summary-tools classify --repo-name "your-favorite/repo"

# 3. 定期更新
star-summary generate --no-cache
```

### 团队使用
```bash
# 1. 配置团队设置
cp config.yaml team-config.yaml

# 2. 生成团队文档
star-summary generate --config team-config.yaml --output docs/

# 3. 自动化部署
# 配置 CI/CD 流水线
```

## 更多资源

- 项目配置：[config.yaml](config.yaml)
- 模板文件：[templates/](templates/)
- 示例输出：[output/README.md](output/README.md)
- 问题反馈：[GitHub Issues](https://github.com/yourusername/star-summary/issues)
