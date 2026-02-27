<script setup lang="ts">
import { onMounted, watch, ref, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLogView } from '../composables/useLogView'

const route = useRoute()
const router = useRouter()
const taskId = route.params.taskId as string
const projectId = route.params.id as string

const { logs, task, loading, error, streaming, autoScroll, init } = useLogView(taskId)

const logContainer = ref<HTMLElement | null>(null)

function scrollToBottom() {
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
}

function onScroll() {
  if (!logContainer.value) return
  const { scrollTop, scrollHeight, clientHeight } = logContainer.value
  autoScroll.value = scrollHeight - scrollTop - clientHeight < 40
}

watch(logs, () => {
  if (autoScroll.value) {
    nextTick(scrollToBottom)
  }
}, { deep: true })

onMounted(async () => {
  await init()
  nextTick(scrollToBottom)
})

function formatTs(ts: string): string {
  try {
    const d = new Date(ts)
    const h = String(d.getHours()).padStart(2, '0')
    const m = String(d.getMinutes()).padStart(2, '0')
    const s = String(d.getSeconds()).padStart(2, '0')
    const ms = String(d.getMilliseconds()).padStart(3, '0')
    return `${h}:${m}:${s}.${ms}`
  } catch {
    return ts
  }
}
</script>

<template>
  <div class="log-page">
    <!-- 顶栏 -->
    <header class="log-header">
      <nav class="breadcrumb">
        <button class="bc-link" @click="router.push('/')">项目列表</button>
        <span class="bc-sep">›</span>
        <button class="bc-link" @click="router.push(`/project/${projectId}`)">看板</button>
        <span class="bc-sep">›</span>
        <button class="bc-link" @click="router.push(`/project/${projectId}/task/${taskId}`)">任务详情</button>
        <span class="bc-sep">›</span>
        <span class="bc-current">执行日志</span>
      </nav>

      <div class="header-right">
        <span v-if="streaming" class="stream-badge">
          <span class="pulse-dot"></span>实时流
        </span>
        <span v-else-if="task" class="idle-badge">
          {{ task.status === 'in_progress' ? '连接中' : '已结束' }}
        </span>
      </div>
    </header>

    <!-- 任务信息栏 -->
    <div v-if="task" class="task-bar">
      <span class="task-type" :class="task.type">{{ task.type === 'feature' ? 'FEAT' : 'BUG' }}</span>
      <span class="task-title">{{ task.title }}</span>
      <span class="task-status" :class="task.status">{{ task.status }}</span>
    </div>

    <!-- 主内容 -->
    <main class="log-main">
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

      <!-- 日志终端 -->
      <div v-else class="terminal-wrap">
        <div class="terminal-titlebar">
          <div class="term-dots">
            <span class="dot red"></span>
            <span class="dot yellow"></span>
            <span class="dot green"></span>
          </div>
          <span class="term-label">{{ task?.title ?? `task:${taskId}` }}</span>
          <span class="line-count">{{ logs.length }} 行</span>
        </div>

        <div
          ref="logContainer"
          class="terminal-body"
          @scroll="onScroll"
        >
          <!-- 空状态 -->
          <div v-if="logs.length === 0" class="empty-term">
            <span class="empty-icon">○</span>
            <span>暂无日志</span>
          </div>

          <!-- 日志行 -->
          <div
            v-for="(entry, idx) in logs"
            :key="idx"
            class="log-line"
            :class="entry.stream"
          >
            <span class="log-ts">{{ formatTs(entry.ts) }}</span>
            <span class="log-stream-tag" :class="entry.stream">
              {{ entry.stream === 'stdout' ? 'OUT' : 'ERR' }}
            </span>
            <span class="log-content">{{ entry.line }}</span>
          </div>

          <!-- SSE 游标 -->
          <div v-if="streaming" class="cursor-line">
            <span class="blink-cursor">▌</span>
          </div>
        </div>

        <!-- 自动滚动提示 -->
        <div v-if="!autoScroll && logs.length > 0" class="scroll-hint" @click="autoScroll = true; nextTick(scrollToBottom)">
          <span>↓ 跳到底部</span>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

.log-page {
  min-height: 100vh;
  background: #0d1117;
  color: #e6edf3;
  font-family: 'DM Sans', sans-serif;
  display: flex;
  flex-direction: column;
}

/* ── 顶栏 ── */
.log-header {
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

.header-right { display: flex; align-items: center; gap: 8px; }

.stream-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #0d2b1a;
  border: 1px solid #2ea043;
  color: #3fb950;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.04em;
}
.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #3fb950;
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.75); }
}

.idle-badge {
  font-size: 12px;
  color: #8b949e;
  border: 1px solid #30363d;
  padding: 3px 10px;
  border-radius: 20px;
}

/* ── 任务栏 ── */
.task-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 24px;
  background: #0d1117;
  border-bottom: 1px solid #21262d;
  flex-shrink: 0;
}

.task-type {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 2px 7px;
  border-radius: 4px;
}
.task-type.feature { background: #1f3045; color: #58a6ff; }
.task-type.bug { background: #3d1a1a; color: #ff7b72; }

.task-title {
  font-size: 14px;
  font-weight: 500;
  color: #e6edf3;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-status {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  padding: 2px 8px;
  border-radius: 12px;
}
.task-status.pending { background: #21262d; color: #8b949e; }
.task-status.in_progress { background: #1f3045; color: #58a6ff; }
.task-status.pending_review { background: #2d2208; color: #d29922; }
.task-status.completed { background: #0d2b1a; color: #3fb950; }
.task-status.failed { background: #3d1a1a; color: #ff7b72; }
.task-status.cancelled { background: #21262d; color: #6e7681; }

/* ── 主内容 ── */
.log-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px 24px;
  min-height: 0;
}

.state-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
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
.error-icon { font-size: 28px; color: #ff7b72; }
.error-text { color: #ff7b72; }

/* ── 终端容器 ── */
.terminal-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #30363d;
  border-radius: 8px;
  overflow: hidden;
  min-height: 0;
  position: relative;
}

.terminal-titlebar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  background: #161b22;
  border-bottom: 1px solid #21262d;
  flex-shrink: 0;
}
.term-dots { display: flex; gap: 6px; }
.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.dot.red { background: #ff5f57; }
.dot.yellow { background: #febc2e; }
.dot.green { background: #28c840; }

.term-label {
  flex: 1;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: #8b949e;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.line-count {
  font-size: 11px;
  color: #484f58;
  font-family: 'JetBrains Mono', monospace;
}

.terminal-body {
  flex: 1;
  overflow-y: auto;
  background: #010409;
  padding: 12px 0;
  min-height: 300px;
  scrollbar-width: thin;
  scrollbar-color: #21262d transparent;
}
.terminal-body::-webkit-scrollbar { width: 6px; }
.terminal-body::-webkit-scrollbar-track { background: transparent; }
.terminal-body::-webkit-scrollbar-thumb { background: #21262d; border-radius: 3px; }

/* ── 空状态 ── */
.empty-term {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 60px 0;
  color: #484f58;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
}
.empty-icon { font-size: 24px; }

/* ── 日志行 ── */
.log-line {
  display: flex;
  align-items: baseline;
  gap: 0;
  padding: 1px 14px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12.5px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-all;
}
.log-line:hover { background: rgba(255,255,255,0.03); }

.log-ts {
  color: #484f58;
  font-size: 11px;
  min-width: 96px;
  flex-shrink: 0;
  user-select: none;
}

.log-stream-tag {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 0 5px;
  margin: 0 8px 0 4px;
  border-radius: 3px;
  flex-shrink: 0;
  line-height: 16px;
  align-self: center;
  user-select: none;
}
.log-stream-tag.stdout { background: #21262d; color: #8b949e; }
.log-stream-tag.stderr { background: #3d1a1a; color: #ff7b72; }

.log-content { color: #c9d1d9; flex: 1; }
.log-line.stderr .log-content { color: #ffa07a; }

/* ── SSE 游标 ── */
.cursor-line {
  padding: 2px 14px;
  font-family: 'JetBrains Mono', monospace;
}
.blink-cursor {
  color: #3fb950;
  font-size: 14px;
  animation: blink 1s step-end infinite;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* ── 跳到底部提示 ── */
.scroll-hint {
  position: absolute;
  bottom: 14px;
  left: 50%;
  transform: translateX(-50%);
  background: #1f6feb;
  color: #fff;
  font-size: 12px;
  font-weight: 500;
  padding: 5px 14px;
  border-radius: 20px;
  cursor: pointer;
  box-shadow: 0 2px 12px rgba(31,111,235,0.4);
  transition: background 0.15s;
  z-index: 10;
}
.scroll-hint:hover { background: #388bfd; }
</style>
