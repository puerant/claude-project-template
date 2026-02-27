<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTaskDetail } from '../composables/useTaskDetail'
import type { TaskStatus } from '../types'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id as string
const taskId = route.params.taskId as string

const { task, loading, error, operating, fetchTask, execute, cancel, reset, review } =
  useTaskDetail(taskId)

const showReview = ref(false)
const reviewResult = ref<'pass' | 'fail'>('pass')
const failedCriteria = ref<string[]>([])
const submitting = ref(false)

onMounted(fetchTask)

function openReview() {
  reviewResult.value = 'pass'
  failedCriteria.value = []
  showReview.value = true
}

function toggleCriteria(c: string) {
  const idx = failedCriteria.value.indexOf(c)
  if (idx === -1) failedCriteria.value.push(c)
  else failedCriteria.value.splice(idx, 1)
}

async function submitReview() {
  submitting.value = true
  await review(reviewResult.value, failedCriteria.value)
  submitting.value = false
  showReview.value = false
}

const STATUS_LABEL: Record<TaskStatus, string> = {
  pending: '待开发', in_progress: '开发中', pending_review: '待 review',
  completed: '已完成', failed: '失败', cancelled: '已取消',
}
const STATUS_CLASS: Record<TaskStatus, string> = {
  pending: 'status-pending', in_progress: 'status-progress',
  pending_review: 'status-review', completed: 'status-done',
  failed: 'status-fail', cancelled: 'status-cancel',
}
const TYPE_LABEL: Record<string, string> = { feature: 'feat', bug: 'bug' }

function fmtDate(iso: string) {
  return new Date(iso).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
  })
}
</script>

<template>
  <div>
    <!-- Breadcrumb -->
    <div class="flex items-center gap-2 mb-6 flex-wrap">
      <button class="breadcrumb-link" @click="router.push('/')">项目列表</button>
      <span class="breadcrumb-sep">/</span>
      <button class="breadcrumb-link" @click="router.push(`/project/${projectId}`)">看板</button>
      <span class="breadcrumb-sep">/</span>
      <span class="breadcrumb-cur">{{ task?.title || taskId }}</span>
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

    <div v-else-if="task" class="detail-layout">
      <!-- Left: info + description -->
      <div class="detail-main">
        <div class="flex items-start gap-3 mb-5">
          <span class="type-badge" :class="`badge-${task.type}`">{{ TYPE_LABEL[task.type] }}</span>
          <h1 class="task-title">{{ task.title }}</h1>
        </div>

        <div class="meta-grid mb-6">
          <div class="meta-item">
            <span class="meta-label">状态</span>
            <span class="status-badge" :class="STATUS_CLASS[task.status]">{{ STATUS_LABEL[task.status] }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">模块</span>
            <span class="meta-value">{{ task.module }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">创建</span>
            <span class="meta-value mono">{{ fmtDate(task.createdAt) }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">更新</span>
            <span class="meta-value mono">{{ fmtDate(task.updatedAt) }}</span>
          </div>
          <div v-if="task.branch" class="meta-item meta-full">
            <span class="meta-label">分支</span>
            <span class="meta-value mono">{{ task.branch }}</span>
          </div>
          <div v-if="task.worktreePath" class="meta-item meta-full">
            <span class="meta-label">Worktree</span>
            <span class="meta-value mono">{{ task.worktreePath }}</span>
          </div>
        </div>

        <div class="section-block">
          <h2 class="section-title">任务描述</h2>
          <pre class="desc-pre">{{ task.description }}</pre>
        </div>
      </div>

      <!-- Right: actions + criteria -->
      <div class="detail-side">
        <div class="section-block mb-4">
          <h2 class="section-title">操作</h2>
          <div class="flex flex-col gap-2">
            <button v-if="task.status === 'pending'"
                    class="btn-action btn-primary-action" :disabled="operating" @click="execute">
              {{ operating ? '执行中…' : '触发执行' }}
            </button>
            <button v-if="task.status === 'pending_review'"
                    class="btn-action btn-primary-action" :disabled="operating" @click="openReview">
              提交 Review
            </button>
            <button v-if="task.status === 'failed'"
                    class="btn-action btn-warn-action" :disabled="operating" @click="reset">
              {{ operating ? '重置中…' : '重置为待开发' }}
            </button>
            <button v-if="['pending','in_progress','pending_review'].includes(task.status)"
                    class="btn-action btn-ghost-action" :disabled="operating" @click="cancel">
              {{ operating ? '取消中…' : '取消任务' }}
            </button>
            <button class="btn-action btn-ghost-action"
                    @click="router.push(`/project/${projectId}/task/${taskId}/log`)">
              查看执行日志
            </button>
          </div>
        </div>

        <div class="section-block">
          <h2 class="section-title">验收标准</h2>
          <ul class="criteria-list">
            <li v-for="c in task.acceptanceCriteria" :key="c" class="criteria-item">
              <span class="criteria-dot" :class="task.status === 'completed' ? 'dot-done' : 'dot-pending'"></span>
              <span class="criteria-text">{{ c }}</span>
            </li>
          </ul>
          <p v-if="task.acceptanceCriteria.length === 0" class="no-criteria">暂无验收标准</p>
        </div>

        <div v-if="task.bugReportPath" class="section-block mt-4">
          <h2 class="section-title">关联 Bug 报告</h2>
          <p class="meta-value mono" style="font-size:0.75rem;">{{ task.bugReportPath }}</p>
        </div>
      </div>
    </div>

    <!-- Review modal -->
    <Teleport to="body">
      <div v-if="showReview" class="modal-backdrop" @click.self="showReview = false">
        <div class="modal-box">
          <div class="flex items-center justify-between mb-4">
            <h2 class="modal-title">提交 Review</h2>
            <button class="icon-btn" @click="showReview = false">
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
          <div v-if="reviewResult === 'fail'" class="mb-4">
            <p class="field-label mb-2">选择未通过的验收标准</p>
            <div class="flex flex-col gap-2">
              <label v-for="c in task!.acceptanceCriteria" :key="c" class="flex items-start gap-2 cursor-pointer">
                <input type="checkbox" :checked="failedCriteria.includes(c)" @change="toggleCriteria(c)"
                       style="accent-color:#ff7b72;width:14px;height:14px;margin-top:2px;flex-shrink:0;" />
                <span style="font-size:0.8125rem;color:#c9d1d9;line-height:1.5;">{{ c }}</span>
              </label>
            </div>
          </div>
          <button class="btn-action btn-primary-action w-full"
                  :disabled="submitting || (reviewResult === 'fail' && failedCriteria.length === 0)"
                  @click="submitReview">
            {{ submitting ? '提交中…' : '确认提交' }}
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

.error-bar { display: flex; align-items: center; gap: 8px; padding: 10px 14px; border-radius: 8px; background: #3d1c1c; border: 1px solid rgba(248,81,73,0.25); color: #ff7b72; font-size: 0.8125rem; }
.spinner { width: 15px; height: 15px; border-radius: 50%; border: 2px solid #1f6feb; border-top-color: transparent; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.detail-layout { display: grid; gap: 20px; grid-template-columns: 1fr 260px; align-items: start; }
@media (max-width: 860px) { .detail-layout { grid-template-columns: 1fr; } }

.type-badge { font-size: 0.6875rem; padding: 2px 8px; border-radius: 5px; font-family: 'JetBrains Mono', monospace; font-weight: 500; flex-shrink: 0; margin-top: 3px; }
.badge-feature { background: #1a2d45; color: #58a6ff; }
.badge-bug     { background: #3d1c1c; color: #ff7b72; }

.task-title { font-size: 1.25rem; font-weight: 600; color: #e6edf3; letter-spacing: -0.02em; line-height: 1.4; }

.meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.meta-full { grid-column: 1 / -1; }
.meta-item { display: flex; flex-direction: column; gap: 2px; }
.meta-label { font-size: 0.6875rem; font-weight: 500; color: #7d8590; text-transform: uppercase; letter-spacing: 0.04em; }
.meta-value { font-size: 0.8125rem; color: #c9d1d9; word-break: break-all; }

.status-badge { display: inline-flex; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500; width: fit-content; }
.status-pending  { background: #21262d; color: #8b949e; }
.status-progress { background: #1a2d45; color: #58a6ff; }
.status-review   { background: #2d2200; color: #d29922; }
.status-done     { background: #1a2d1a; color: #3fb950; }
.status-fail     { background: #3d1c1c; color: #ff7b72; }
.status-cancel   { background: #21262d; color: #484f58; }

.section-block { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 16px; }
.section-title { font-size: 0.6875rem; font-weight: 600; color: #7d8590; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }

.desc-pre { font-size: 0.8125rem; color: #c9d1d9; line-height: 1.7; white-space: pre-wrap; word-break: break-word; font-family: 'JetBrains Mono', monospace; margin: 0; }

.criteria-list { display: flex; flex-direction: column; gap: 8px; list-style: none; padding: 0; margin: 0; }
.criteria-item { display: flex; align-items: flex-start; gap: 8px; }
.criteria-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; }
.dot-done    { background: #3fb950; }
.dot-pending { background: transparent; border: 1.5px solid #484f58; }
.criteria-text { font-size: 0.8125rem; color: #c9d1d9; line-height: 1.5; }
.no-criteria { font-size: 0.75rem; color: #484f58; }

.btn-action { display: flex; align-items: center; justify-content: center; padding: 8px 14px; border-radius: 8px; font-size: 0.8125rem; font-weight: 500; cursor: pointer; border: 1px solid transparent; transition: background 0.15s; width: 100%; }
.btn-action:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary-action { background: #1f6feb; color: #fff; border-color: rgba(56,139,253,0.25); }
.btn-primary-action:hover:not(:disabled) { background: #388bfd; }
.btn-warn-action { background: #2d2200; color: #d29922; border-color: rgba(210,153,34,0.3); }
.btn-warn-action:hover:not(:disabled) { background: #3d3000; }
.btn-ghost-action { background: #21262d; color: #8b949e; border-color: #30363d; }
.btn-ghost-action:hover:not(:disabled) { background: #2d333b; }

.modal-backdrop { position: fixed; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.65); backdrop-filter: blur(4px); z-index: 50; padding: 16px; }
.modal-box { width: 100%; max-width: 440px; background: #161b22; border: 1px solid #30363d; border-radius: 14px; padding: 22px; box-shadow: 0 20px 48px rgba(0,0,0,0.5); }
.modal-title { font-size: 1rem; font-weight: 600; color: #e6edf3; letter-spacing: -0.02em; }

.icon-btn { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #7d8590; background: transparent; border: none; cursor: pointer; transition: color 0.15s, background 0.15s; }
.icon-btn:hover { color: #c9d1d9; background: #21262d; }

.result-btn { flex: 1; padding: 7px; border-radius: 7px; font-size: 0.8125rem; font-weight: 500; cursor: pointer; border: 1px solid #30363d; transition: all 0.15s; }
.result-pass-active { background: #1a2d1a; color: #3fb950; border-color: rgba(63,185,80,0.35); }
.result-fail-active { background: #3d1c1c; color: #ff7b72; border-color: rgba(255,123,114,0.35); }
.result-inactive { background: #21262d; color: #8b949e; }
.field-label { font-size: 0.75rem; font-weight: 500; color: #8b949e; }
</style>
