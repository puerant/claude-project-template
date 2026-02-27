<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBugList } from '../composables/useBugList'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id as string

const { bugs, loading, error, fetchBugs } = useBugList(projectId)

onMounted(fetchBugs)

function formatDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })
      + ' ' + d.toLocaleTimeString('zh-CN', { hour12: false, hour: '2-digit', minute: '2-digit' })
  } catch {
    return iso
  }
}
</script>

<template>
  <div class="bug-page">
    <!-- 顶栏 -->
    <header class="bug-header">
      <nav class="breadcrumb">
        <button class="bc-link" @click="router.push('/')">项目列表</button>
        <span class="bc-sep">›</span>
        <button class="bc-link" @click="router.push(`/project/${projectId}`)">看板</button>
        <span class="bc-sep">›</span>
        <span class="bc-current">Bug 列表</span>
      </nav>
      <span class="bug-count" v-if="!loading && !error">{{ bugs.length }} 条</span>
    </header>

    <!-- 主内容 -->
    <main class="bug-main">
      <!-- 加载中 -->
      <div v-if="loading" class="state-center">
        <div class="spinner"></div>
        <span class="state-text">加载中…</span>
      </div>

      <!-- 错误 -->
      <div v-else-if="error" class="state-center">
        <span class="error-icon">✕</span>
        <span class="state-text error-text">{{ error }}</span>
      </div>

      <!-- 空状态 -->
      <div v-else-if="bugs.length === 0" class="state-center">
        <span class="empty-icon">✓</span>
        <span class="state-text">暂无 Bug 报告</span>
        <span class="state-sub">所有任务执行正常</span>
      </div>

      <!-- Bug 列表 -->
      <ul v-else class="bug-list">
        <li
          v-for="bug in bugs"
          :key="bug.filename"
          class="bug-card"
          @click="router.push(`/project/${projectId}/task/${bug.taskId}`)"
        >
          <div class="card-left">
            <span class="bug-label">BUG</span>
          </div>

          <div class="card-body">
            <div class="card-top">
              <span class="bug-filename">{{ bug.filename }}</span>
              <span class="bug-date">{{ formatDate(bug.createdAt) }}</span>
            </div>
            <div class="card-meta">
              <span class="meta-tag module">{{ bug.module }}</span>
              <span class="meta-tag feature">{{ bug.feature }}</span>
            </div>
            <p class="bug-desc">{{ bug.description }}</p>
          </div>

          <div class="card-right">
            <span class="arrow">›</span>
          </div>
        </li>
      </ul>
    </main>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

.bug-page {
  min-height: 100vh;
  background: #0d1117;
  color: #e6edf3;
  font-family: 'DM Sans', sans-serif;
  display: flex;
  flex-direction: column;
}

/* ── 顶栏 ── */
.bug-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  border-bottom: 1px solid #21262d;
  background: #161b22;
  flex-shrink: 0;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}
.bc-link {
  background: none;
  border: none;
  color: #58a6ff;
  cursor: pointer;
  padding: 0;
  font-size: 13px;
  font-family: inherit;
}
.bc-link:hover { text-decoration: underline; }
.bc-sep { color: #484f58; }
.bc-current { color: #8b949e; }

.bug-count {
  font-size: 12px;
  color: #8b949e;
  border: 1px solid #30363d;
  padding: 3px 10px;
  border-radius: 20px;
  font-family: 'JetBrains Mono', monospace;
}

/* ── 主内容 ── */
.bug-main {
  flex: 1;
  padding: 24px;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
}

.state-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 80px 0;
}
.spinner {
  width: 28px;
  height: 28px;
  border: 2px solid #21262d;
  border-top-color: #58a6ff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.state-text { font-size: 14px; color: #8b949e; }
.state-sub { font-size: 12px; color: #484f58; }
.error-icon { font-size: 28px; color: #ff7b72; }
.error-text { color: #ff7b72; }
.empty-icon { font-size: 32px; color: #3fb950; }

/* ── Bug 列表 ── */
.bug-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bug-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 8px;
  padding: 16px 18px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.bug-card:hover {
  border-color: #ff7b72;
  background: #1a1117;
}

.card-left { padding-top: 2px; flex-shrink: 0; }
.bug-label {
  display: inline-block;
  background: #3d1a1a;
  color: #ff7b72;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
}

.card-body { flex: 1; min-width: 0; }

.card-top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 6px;
}
.bug-filename {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: #8b949e;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}
.bug-date {
  font-size: 11px;
  color: #484f58;
  flex-shrink: 0;
  font-family: 'JetBrains Mono', monospace;
}

.card-meta {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.meta-tag {
  font-size: 11px;
  font-weight: 500;
  padding: 1px 8px;
  border-radius: 12px;
}
.meta-tag.module { background: #1f3045; color: #58a6ff; }
.meta-tag.feature { background: #21262d; color: #8b949e; }

.bug-desc {
  font-size: 13px;
  color: #c9d1d9;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-right { flex-shrink: 0; padding-top: 2px; }
.arrow {
  font-size: 20px;
  color: #484f58;
  transition: color 0.15s;
}
.bug-card:hover .arrow { color: #ff7b72; }
</style>
