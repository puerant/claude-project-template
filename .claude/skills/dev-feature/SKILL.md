# dev-feature

将下一个待完成任务从设计到合并的完整开发流程自动化执行。

## 用法

```
/dev-feature [feature-number feature-name]
```

- **无参数**：自动读取 `docs/开发文档/任务清单.md`，提取下一个待完成任务
- **有参数**：例如 `/dev-feature 015 project-list-page`，直接指定功能编号和名称

---

## 执行流程

### 第一步：确认任务

读取 `docs/开发文档/任务清单.md`，确认下一个待完成任务的：
- 功能编号（NNN，三位数字，如 015）
- 功能名称（kebab-case，如 project-list-page）
- 验收标准

如果有参数 `$ARGUMENTS`，则从参数中解析功能编号和名称，跳过自动读取。

---

### 第二步：创建功能设计文档

在 `docs/开发文档/feature/NNN-feature-name/` 下创建三个文档：

**spec.md**（WHAT — 做什么）
```markdown
# NNN: Feature Name

## 需求来源
（关联的 PRD 章节或任务清单条目）

## 功能描述
（一句话描述功能）

## 验收标准
- [ ] 标准1
- [ ] 标准2

## 接口约定
（涉及的 API 端点或组件接口）
```

**plan.md**（HOW — 怎么做）
```markdown
# NNN: Feature Name — 实现方案

## 技术方案
（关键设计决策，分层架构说明）

## 文件清单
（需要新建或修改的文件列表）

## 依赖关系
（前置完成的功能或外部依赖）
```

**tasks.md**（DO — 原子任务）
```markdown
# NNN: Feature Name — 原子任务

| 编号 | 文件 | 操作 | 状态 |
|------|------|------|------|
| T-01 | path/to/file.py | 创建 XxxService | pending |
| T-02 | path/to/router.py | 创建路由 | pending |
```

> 每个原子任务只操作**一个文件**

---

### 第三步：提交文档到 master

```bash
git add docs/开发文档/feature/NNN-feature-name/
git commit -m "docs: NNN feature-name 功能设计文档"
```

---

### 第四步：创建分支与 worktree

```bash
git worktree add .worktrees/feat/NNN-feature-name -b feat/NNN-feature-name
```

worktree 路径：`.worktrees/feat/NNN-feature-name`

---

### 第五步：在 worktree 中执行原子任务

切换工作目录到 `.worktrees/feat/NNN-feature-name`，逐一执行 tasks.md 中的原子任务：

- 每完成一个任务，将 tasks.md 中对应行状态改为 `done`
- 每次只操作一个文件，避免交叉修改
- 遵循项目编码规范（见 CLAUDE.md）

**后端任务规范**（Python / FastAPI）：
- 新建 Service → 新建 Router → 注册到 main.py → 验证导入

**前端任务规范**（Vue3 / TypeScript）：
- 新建 composable → 新建组件/页面 → 注册路由 → 验证构建

---

### 第六步：验证验收标准

**后端验证**：
```bash
cd .worktrees/feat/NNN-feature-name/backend
python -c "from app.main import app; print('OK')"
```

**前端验证**：
```bash
cd .worktrees/feat/NNN-feature-name/frontend/portal
npm run build
```

所有验收标准逐一确认通过后，继续下一步。

---

### 第七步：在 worktree 中提交代码

```bash
cd .worktrees/feat/NNN-feature-name
git add <具体文件，不使用 git add -A>
git commit -m "feat: NNN feature-name 简短描述"
```

---

### 第八步：合并到 master 并清理

```bash
# 回到主仓库
git merge feat/NNN-feature-name --no-ff -m "feat: merge NNN-feature-name"

# 清理 worktree（Windows 兼容方案）
git worktree remove .worktrees/feat/NNN-feature-name --force 2>/dev/null || git worktree prune
git branch -d feat/NNN-feature-name
```

---

### 第九步：更新任务清单

编辑 `docs/开发文档/任务清单.md`：
- 将已完成功能的状态更新为"已完成"
- 列出本次完成的具体内容
- 标注下一个待完成任务

提交：
```bash
git add docs/开发文档/任务清单.md
git commit -m "docs: 更新任务清单，NNN 已完成"
```

---

### 第十步：推送到远程

```bash
git push origin master
```

---

## 注意事项

1. **文件暂存原则**：`git add` 时指定具体文件路径，不使用 `git add .` 或 `git add -A`
2. **Windows worktree 清理**：优先 `--force`，失败则用 `git worktree prune`
3. **验证前安装依赖**：Python 项目验证前执行 `pip install -r requirements.txt -q`
4. **禁止跨文件原子任务**：tasks.md 中每个 T-XX 只能操作一个文件
5. **禁止直接推送到 main**：本项目 main 分支只接受 PR，日常推送到 master

---

## 快速检查清单

```
[ ] 读取任务清单，确认功能编号和名称
[ ] 创建 spec.md / plan.md / tasks.md
[ ] git commit docs 到 master
[ ] git worktree add 创建隔离工作区
[ ] 逐一执行原子任务（每次一个文件）
[ ] 验证验收标准通过
[ ] 在 worktree 中 git commit
[ ] 合并到 master
[ ] 清理 worktree 和分支
[ ] 更新任务清单 + git commit
[ ] git push origin master
```
