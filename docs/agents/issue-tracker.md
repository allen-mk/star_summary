# Issue tracker: GitHub

本仓库的议题与 Spec 存放在 GitHub Issues。所有操作使用 `gh` CLI。

## 约定

- **创建议题**：`gh issue create --title "..." --body "..."`。多行 body 用 heredoc。
- **读取议题**：`gh issue view <number> --comments`，可用 `jq` 过滤 comments 并一并取 labels。
- **列出议题**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，配合适当的 `--label` 与 `--state`。
- **评论议题**：`gh issue comment <number> --body "..."`
- **添加 / 移除标签**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **关闭**：`gh issue close <number> --comment "..."`

从 `git remote -v` 推断仓库；在 clone 内运行时 `gh` 会自动推断。

## Pull requests 作为 triage 表面

**PRs as a request surface: no。** _（若本仓库把外部 PR 当作 feature request，设为 `yes`；`matt-triage` 会读此开关。）_

设为 `yes` 时，PR 走与议题相同的标签与状态，使用 `gh pr` 等价命令：

- **读取 PR**：`gh pr view <number> --comments`，以及 `gh pr diff <number>` 看 diff。
- **列出待 triage 的外部 PR**：`gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`，只保留 `authorAssociation` 为 `CONTRIBUTOR`、`FIRST_TIME_CONTRIBUTOR` 或 `NONE`（丢掉 `OWNER` / `MEMBER` / `COLLABORATOR`）。
- **评论 / 标签 / 关闭**：`gh pr comment`、`gh pr edit --add-label`/`--remove-label`、`gh pr close`。

GitHub 的 issue 与 PR 共用一套编号，所以裸 `#42` 可能是任一者：先 `gh pr view 42`，失败再 `gh issue view 42`。

## 当技能说「发布到 issue tracker」

创建一条 GitHub issue。

## 当技能说「拉取相关 ticket」

运行 `gh issue view <number> --comments`。

## Wayfinding 操作

供 `matt-wayfinder` 使用。**map** 是一条议题，**child** 议题是 tickets。

- **Map**：带 `matt-wayfinder:map` 标签的单条议题，正文含 Notes / Decisions-so-far / Fog。`gh issue create --label matt-wayfinder:map`。
- **Child ticket**：作为 GitHub sub-issue 链到 map 的议题（对 sub-issues 端点用 `gh api`）。若未启用 sub-issues，把 child 加进 map 正文的 task list，并在 child 正文顶部写 `Part of #<map>`。标签：`matt-wayfinder:<type>`（`matt-research` / `matt-prototype` / `matt-grilling` / `task`）。认领后把 ticket 指派给驱动开发者。
- **Blocking**：GitHub **原生 issue dependencies**，规范且 UI 可见。添加边：`gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`，其中 `<blocker-db-id>` 是 blocker 的数字 **database id**（`gh api repos/<owner>/<repo>/issues/<n> --jq .id`，**不是** `#number` 或 `node_id`）。GitHub 报告 `issue_dependencies_summary.blocked_by`（仅开放 blocker，即实时门禁）。若依赖不可用，回退为 child 正文顶部的 `Blocked by: #<n>, #<n>` 行。当每个 blocker 都关闭时，ticket 才 unblocked。
- **Frontier 查询**：列出 map 的开放 children（`gh issue list --state open`，按 map 的 sub-issues / task list 限定范围），丢掉仍有开放 blocker（`issue_dependencies_summary.blocked_by > 0`，或 `Blocked by` 行中仍开放的议题）或已有 assignee 的项；按 map 顺序取第一个。
- **Claim**：`gh issue edit <n> --add-assignee @me`，会话的首次写入。
- **Resolve**：`gh issue comment <n> --body "<answer>"`，然后 `gh issue close <n>`，再把 context 指针（摘要 + 链接）追加到 map 的 Decisions-so-far。
