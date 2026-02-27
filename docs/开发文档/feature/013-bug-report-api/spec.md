# 功能需求：Bug 报告列表接口

> 任务编号：M2-T10
> 模块：后端服务

---

## 用户故事

作为开发者，我需要在项目详情页查看该项目下所有 Bug 报告的摘要列表，以便追踪哪些功能存在未修复的问题。

---

## 功能描述

### 3.1 接口定义

```
GET /api/projects/{projectId}/bugs
```

扫描被管理项目 `docs/bug/` 目录下的所有 `.md` 文件，解析文件头信息，返回 Bug 报告摘要列表，按 `createdAt` 降序排列。

### 3.2 Bug 报告文件命名规则

文件名格式（由 FileWriteService 生成）：

```
<YYYY-MM-DD>-<模块>-<功能>-<简短描述>.md
```

示例：`2026-02-27-用户模块-登录功能-错误提示未显示.md`

### 3.3 解析规则

从文件名提取：

- `createdAt`：文件名前 10 字符（YYYY-MM-DD）
- `module`：日期后第 1 段（按 `-` 分割，最多 3 份）
- `feature`：日期后第 2 段
- `description`：日期后第 3 段（去除 `.md`）

从文件内容提取：

- `taskId`：匹配 `**任务 ID**：<uuid>` 行

### 3.4 返回结构

```typescript
interface BugReport {
  filename: string       // 文件名（含 .md）
  relativePath: string   // 相对项目根目录的路径
  taskId: string         // 关联任务 ID
  module: string         // 所属模块
  feature: string        // 功能名
  description: string    // 简短描述
  createdAt: string      // 创建日期（YYYY-MM-DD）
}
```

---

## 验收标准

- [ ] `GET /api/projects/{projectId}/bugs` 返回 `BugReport[]`，按 `createdAt` 降序
- [ ] `docs/bug/` 目录不存在时返回空列表（不报错）
- [ ] 正确从文件名解析 module / feature / description / createdAt
- [ ] 正确从文件内容解析 taskId
- [ ] 项目不存在时返回 404

---

## 边界情况

| 场景 | 预期行为 |
| ---- | -------- |
| `docs/bug/` 不存在 | 返回 `[]` |
| Bug 报告文件内容缺少任务 ID 行 | `taskId` 返回空字符串 |
| 文件名格式不符合规范 | 跳过该文件 |
| 项目不存在 | 返回 404 |
