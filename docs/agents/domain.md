# Domain Docs

工程技能在探索代码库时应如何消费本仓库的 domain 文档。

## 探索前先读这些

- 根目录的 **`CONTEXT.md`**，或
- 若存在根目录 **`CONTEXT-MAP.md`**：它指向每个 context 的 `CONTEXT.md`。读与当前话题相关的那些。
- **`docs/adr/`**：读触及你即将动手区域的 ADR。多 context 仓库中，也检查 `src/<context>/docs/adr/` 中的 context 级决策。

若这些文件不存在，**静默继续**。不要标记缺失，也不要建议事先创建。`matt-domain-modeling` 技能（经由 `matt-grill-with-docs` 与 `matt-improve-codebase-architecture` 触及）会在术语或决策真正敲定时懒创建它们。

## 文件结构

单 context 仓库（多数仓库）：

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

多 context 仓库（根目录存在 `CONTEXT-MAP.md`）：

```
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← 系统级决策
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                  ← context 专属决策
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## 使用 glossary 的词汇

当输出命名某个 domain 概念（议题标题、重构提案、假设、测试名）时，使用 `CONTEXT.md` 中定义的术语。不要漂到 glossary 明确 `_Avoid_` 的同义词。

若所需概念尚不在 glossary 中，这是信号：要么你在发明项目不用的语言（请重新考虑），要么存在真实缺口（记下来交给 `matt-domain-modeling`）。

## 标出 ADR 冲突

若输出与已有 ADR 矛盾，显式摊开，而不是静默覆盖：

> _与 ADR-0007（event-sourced orders）矛盾，但值得重开，因为……_
