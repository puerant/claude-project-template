# 技术方案：前端项目初始化

> 任务编号：M3-T01
> 模块：前端

---

## 架构设计

### 目录结构

```
frontend/portal/
├── index.html
├── vite.config.ts          ← 代理配置
├── tailwind.config.js      ← Tailwind 内容路径
├── postcss.config.js
├── package.json
└── src/
    ├── main.ts             ← 挂载 App，注册 router
    ├── App.vue             ← 根组件（router-view + 全局导航）
    ├── style.css           ← Tailwind 指令
    ├── types/
    │   └── index.ts        ← 所有 TS 类型定义
    ├── api/
    │   ├── client.ts       ← axios 实例
    │   ├── projects.ts
    │   ├── tasks.ts
    │   ├── logs.ts
    │   └── bugs.ts
    ├── router/
    │   └── index.ts        ← 5 条路由
    ├── views/
    │   ├── ProjectList.vue
    │   ├── ProjectBoard.vue
    │   ├── TaskDetail.vue
    │   ├── LogView.vue
    │   └── BugList.vue
    ├── components/         ← 后续功能特性填充
    └── composables/        ← 后续功能特性填充
```

### 依赖

| 包 | 版本 | 用途 |
| -- | ---- | ---- |
| `vue-router` | 4.x | SPA 路由 |
| `axios` | 1.x | HTTP 客户端 |
| `tailwindcss` | 3.x | 样式框架 |
| `postcss` | - | Tailwind 处理器 |
| `autoprefixer` | - | CSS 兼容前缀 |

---

## 关键配置

### Vite 代理（vite.config.ts）

```ts
server: {
  proxy: {
    '/api': 'http://localhost:8765'
  }
}
```

### Axios 实例（src/api/client.ts）

```ts
import axios from 'axios'

export const client = axios.create({
  baseURL: '/api',
  timeout: 10000,
})
```

### Router（src/router/index.ts）

History 模式，未匹配路由重定向到 `/`。

---

## 任务拆分原则

- T-01：运行脚手架命令（1 次 npm create）
- T-02：安装额外依赖（1 次 npm install）
- T-03 ~ T-09：每个文件独立修改/创建
