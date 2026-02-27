<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskBoard } from '../composables/useTaskBoard'
import { getProjects } from '../api/projects'
import type { Task, TaskStatus } from '../types'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id as string

const { columns, loading, error, operating, fetchTasks, execute, cancel, reset, review } =
  useTaskBoard(projectId)

const projectName = ref('')

// Review modal state
const reviewTask = ref<Task | null>(null)
const reviewResult = ref<'pass' | 'fail'>('pass')
const failedCriteria = ref<string[]>([])
const submittingReview = ref(false)

onMounted(async () => {
  await fetchTasks()
  try {
    const projects = await getProjects()
    projectName.value = projects.find(p => p.id === projectId)?.name ?? projectId
  } catch { /* 项目名获取失败时显示 id */ }
})

function openReview(task: Task) {
  reviewTask.value = task
  reviewResult.value = 'pass'
  failedCriteria.value = []
}

function toggleCriteria(c: string) {
  const idx = failedCriteria.value.indexOf(c)
  if (idx === -1) failedCriteria.value.push(c)
  else failedCriteria.value.splice(idx, 1)
}

async function submitReview() {
  if (!reviewTask.value) return
  submittingReview.value = true
  await review(reviewTask.value.id, reviewResult.value, failedCriteria.value)
  submittingReview.value = false
  reviewTask.value = null
}

const COLUMN_LABELS: Record<TaskStatus, string> = {
  pending: '待开发',
  in_progress: '开发中',
  pending_review: '待 review',
  completed: '已完成',
  failed: '失败',
  cancelled: '已取消',
}

const TYPE_LABEL: Record<string, string> = { feature: 'feat', bug: 'bug' }

function fmtTime(iso: string) {
  return new Date(iso).toLocaleDateString('zh-CN', {
    month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}
</script>

<template>
  <div>
    <!-- Breadcrumb header -->
    <div class="flex items-center gap-2 mb-6">
      <button class="breadcrumb-link" @click="router.push('/')">项目列表</button>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-cur">{{ projectName || projectId }}</span>
      <div class="ml-auto flex items-center gap-2">
        <button class="btn-secondary" @click="fetchTasks">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M10.5 6A4.5 4.5 0 1 1 8 2.2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            <path d="M8 1v3h3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          刷新
        </button>
        <button class="btn-secondary" @click="router.push(`/project/${projectId}/bugs`)">Bug 报告</button>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-bar mb-5">
      <svg width="13" height="13" viewBox="0 0 13 13" fill="none" class="shrink-0">
        <circle cx="6.5" cy="6.5" r="5.5" stroke="currentColor" stroke-width="1.3"/>
        <path d="M6.5 3.5v3M6.5 9v.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
      </svg>
      {{ error }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="flex items-center gap-3 muted">
        <div class="spinner"></div>
        <span class="mono text-sm">加载中…</span>
      </div>
    </div>

    <!-- Kanban board -->
    <div v-else class="board">
      <div v-for="col in columns" :key="col.status" class="column">
        <!-- Column header -->
        <div class="col-header">
          <span class="col-dot" :class="`dot-${col.status}`"></span>
          <span class="col-label">{{ COLUMN_LABELS[col.status] }}</span>
          <span class="col-count">{{ col.tasks.length }}</span>
        </div>

        <!-- Task cards -->
        <div class="col-body">
          <div
            v-for="task in col.tasks"
            :key="task.id"
            class="task-card"
            @click="router.push(`/project/${projectId}/task/${task.id}`)"
          >
            <div class="flex items-start gap-2 mb-2">
              <span class="type-badge" :class="`badge-${task.type}`">{{ TYPE_LABEL[task.type] }}</span>
              <span class="task-title">{{ task.title }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="task-meta mono">{{ task.module }}</span>
              <span class="task-meta mono">{{ fmtTime(task.updatedAt) }}</span>
            </div>

            <!-- Actions -->
            <div v-if="col.status !== 'completed' && col.status !== 'cancelled'"
                 class="task-actions" @click.stop>
              <template v-if="col.status === 'pending'">
                <button class="act-btn act-primary" :disabled="operating[task.id]" @click="execute(task.id)">执行</button>
                <button class="act-btn act-ghost"   :disabled="operating[task.id]" @click="cancel(task.id)">取消</button>
              </template>
              <template v-else-if="col.status === 'in_progress'">
                <button class="act-btn act-ghost" :disabled="operating[task.id]" @click="cancel(task.id)">取消</button>
              </template>
              <template v-else-if="col.status === 'pending_review'">
                <button class="act-btn act-primary" :disabled="operating[task.id]" @click="openReview(task)">review</button>
                <button class="act-btn act-ghost"   :disabled="operating[task.id]" @click="cancel(task.id)">取消</button>
              </template>
              <template v-else-if="col.status === 'failed'">
                <button class="act-btn act-warn" :disabled="operating[task.id]" @click="reset(task.id)">重置</button>
              </template>
            </div>
          </div>

          <div v-if="col.tasks.length === 0" class="col-empty">暂无任务</div>
        </div>
      </div>
    </div>

    <!-- Review modal -->
    <Teleport to="body">
      <div v-if="reviewTask" class="modal-backdrop" @click.self="reviewTask = null">
        <div class="modal-box">
          <div class="flex items-start justify-between mb-4">
            <div>
              <h2 class="modal-title">提交 Review</h2>
              <p class="modal-sub mono mt-1">{{ reviewTask.title }}</p>
            </div>
            <button class="icon-btn" @click="reviewTask = null">
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <path d="M1.5 1.5l10 10M11.5 1.5l-10 10" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="flex gap-2 mb-4">
            <button class="result-btn" :class="reviewResult === 'pass' ? 'result-pass-active' : 'result-inactive'"
                    @click="reviewResult = 'pass'; failedCriteria = []">通过</button>
            <button class="result-btn" :class="reviewResult === 'fail' ? 'result-fail-active' : 'result-inactive'"
                    @click="reviewResult = 'fail'">不通过</button>
          </div>

          <div v-if="reviewResult === 'fail'" class="criteria-list mb-4">
            <p class="field-label mb-2">选择未通过的验收标准</p>
            <label v-for="c in reviewTask.acceptanceCriteria" :key="c" class="criteria-item">
              <input type="checkbox" :checked="failedCriteria.includes(c)" @change="toggleCriteria(c)" class="criteria-check" />
              <span class="criteria-text">{{ c }}</span>
            </label>
          </div>

          <button class="btn-primary"
                  :disabled="submittingReview || (reviewResult === 'fail' && failedCriteria.length === 0)"
                  @click="submitReview">
            {{ submittingReview ? '提交中…' : '确认提交' }}
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap');

.mono { font-family: 'JetBrains Mono', monospace; }
.muted { color: #7d8590; }

.breadcrumb-link { font-size: 0.8125rem; color: #58a6ff; background: none; border: none; cursor: pointer; padding: 0; }
.breadcrumb-link:hover { text-decoration: underline; }
.breadcrumb-sep { color: #7d8590; font-size: 0.8125rem; }
.breadcrumb-cur { font-size: 0.8125rem; font-weight: 500; color: #e6edf3; }

.btn-secondary {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 6px 12px; border-radius: 7px; font-size: 0.75rem; font-weight: 500;
  background: #21262d; color: #8b949e; border: 1px solid #30363d; cursor: pointer; transition: background 0.15s;
}
.btn-secondary:hover { background: #2d333b; }

.error-bar {
  display: flex; align-items: center; gap: 8px; padding: 10px 14px; border-radius: 8px;
  background: #3d1c1c; border: 1px solid rgba(248,81,73,0.25); color: #ff7b72; font-size: 0.8125rem;
}

.spinner {
  width: 15px; height: 15px; border-radius: 50%;
  border: 2px solid #1f6feb; border-top-color: transparent; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.board { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 8px; align-items: flex-start; }
.board::-webkit-scrollbar { height: 5px; }
.board::-webkit-scrollbar-track { background: transparent; }
.board::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }

.column { flex: 0 0 220px; min-width: 220px; }

.col-header { display: flex; align-items: center; gap: 6px; padding: 0 2px 10px; }
.col-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-pending        { background: #7d8590; }
.dot-in_progress    { background: #58a6ff; }
.dot-pending_review { background: #d29922; }
.dot-completed      { background: #3fb950; }
.dot-failed         { background: #ff7b72; }
.dot-cancelled      { background: #484f58; }

.col-label { font-size: 0.75rem; font-weight: 600; color: #8b949e; flex: 1; }
.col-count { font-size: 0.6875rem; padding: 1px 6px; border-radius: 10px; background: #21262d; color: #7d8590; font-family: 'JetBrains Mono', monospace; }

.col-body { display: flex; flex-direction: column; gap: 8px; }
.col-empty { padding: 20px 0; text-align: center; font-size: 0.75rem; color: #484f58; border: 1px dashed #21262d; border-radius: 10px; }

.task-card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 12px; cursor: pointer; transition: border-color 0.15s; }
.task-card:hover { border-color: rgba(56,139,253,0.4); }

.type-badge { font-size: 0.625rem; padding: 1px 6px; border-radius: 4px; font-family: 'JetBrains Mono', monospace; font-weight: 500; flex-shrink: 0; margin-top: 1px; }
.badge-feature { background: #1a2d45; color: #58a6ff; }
.badge-bug     { background: #3d1c1c; color: #ff7b72; }

.task-title { font-size: 0.8125rem; font-weight: 500; color: #c9d1d9; line-height: 1.4; }
.task-meta { font-size: 0.625rem; color: #7d8590; }

.task-actions { display: flex; gap: 6px; margin-top: 10px; padding-top: 10px; border-top: 1px solid #21262d; }

.act-btn { padding: 4px 10px; border-radius: 5px; font-size: 0.6875rem; font-weight: 500; cursor: pointer; border: 1px solid transparent; transition: all 0.15s; }
.act-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.act-primary { background: #1f6feb; color: #fff; border-color: rgba(56,139,253,0.25); }
.act-primary:hover:not(:disabled) { background: #388bfd; }
.act-ghost   { background: #21262d; color: #8b949e; border-color: #30363d; }
.act-ghost:hover:not(:disabled) { background: #2d333b; }
.act-warn    { background: #2d2200; color: #d29922; border-color: rgba(210,153,34,0.3); }
.act-warn:hover:not(:disabled) { background: #3d3000; }

.modal-backdrop { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.65); backdrop-filter: blur(4px); z-index: 50; padding: 16px; }
.modal-box { width: 100%; max-width: 440px; background: #161b22; border: 1px solid #30363d; border-radius: 14px; padding: 22px; box-shadow: 0 20px 48px rgba(0,0,0,0.5); }
.modal-title { font-size: 1rem; font-weight: 600; color: #e6edf3; letter-spacing: -0.02em; }
.modal-sub { font-size: 0.75rem; color: #7d8590; }

.icon-btn { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #7d8590; background: transparent; border: none; cursor: pointer; transition: color 0.15s, background 0.15s; }
.icon-btn:hover { color: #c9d1d9; background: #21262d; }

.result-btn { flex: 1; padding: 7px; border-radius: 7px; font-size: 0.8125rem; font-weight: 500; cursor: pointer; border: 1px solid #30363d; transition: all 0.15s; }
.result-pass-active { background: #1a2d1a; color: #3fb950; border-color: rgba(63,185,80,0.35); }
.result-fail-active { background: #3d1c1c; color: #ff7b72; border-color: rgba(255,123,114,0.35); }
.result-inactive { background: #21262d; color: #8b949e; }

.criteria-list { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 0.75rem; font-weight: 500; color: #8b949e; }
.criteria-item { display: flex; align-items: flex-start; gap: 8px; cursor: pointer; }
.criteria-check { width: 14px; height: 14px; margin-top: 2px; flex-shrink: 0; cursor: pointer; accent-color: #ff7b72; }
.criteria-text { font-size: 0.8125rem; color: #c9d1d9; line-height: 1.5; }

.btn-primary {
  display: flex; align-items: center; justify-content: center;
  padding: 9px 16px; border-radius: 8px; font-size: 0.8125rem; font-weight: 500;
  background: #1f6feb; color: #fff; border: 1px solid rgba(56,139,253,0.25);
  cursor: pointer; transition: background 0.15s; width: 100%;
}
.btn-primary:hover:not(:disabled) { background: #388bfd; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
