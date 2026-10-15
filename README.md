# star-summary

自动获取你的 GitHub 星标项目，按规则分类，生成 Markdown 文档和 JSON 数据。

## 安装

```bash
pip install -e .
```

## 配置

在 [GitHub Settings → Tokens](https://github.com/settings/tokens) 创建 Token（勾选 `public_repo`、`read:user`），然后：

```bash
export GITHUB_TOKEN=your_token_here
```

可选：复制 `config.yaml` 调整输出格式与缓存。

## 使用

```bash
# 生成 Markdown（默认输出到 output/README.md）
star-summary generate

# 生成 JSON
star-summary generate --format json

# 同时生成两种格式
star-summary generate --format both --output docs/

# 验证 Token
star-summary validate

# 初始化配置文件
star-summary init
```

## 分类

分类规则由 [`star_summary/taxonomy.yaml`](star_summary/taxonomy.yaml) 定义，是唯一事实来源。新增或调整分类请修改该文件，无需改代码。

## 输出示例

见 [`examples/STAR_README.golden.md`](examples/STAR_README.golden.md)。

## 开发

```bash
pip install -e .[dev]
pytest
```

## 许可

MIT
