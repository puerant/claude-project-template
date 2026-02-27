<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjects } from '../composables/useProjects'
import type { SyncResult } from '../types'

const router = useRouter()
const { projects, loading, error, fetchProjects, addProject, removeProject, sync } = useProjects()

const showModal = ref(false)
const newName = ref('')
const newPath = ref('')
const submitting = ref(false)
const syncResults = ref<Record<string, SyncResult & { ts: number }>>({})
const syncing = ref<Record<string, boolean>>({})

onMounted(fetchProjects)

async function handleAdd() {
  if (!newName.value.trim() || !newPath.value.trim()) return
  submitting.value = true
  const result = await addProject(newName.value.trim(), newPath.value.trim())
  submitting.value = false
  if (result) {
    showModal.value = false
    newName.value = ''
    newPath.value = ''
  }
}

async function handleDelete(id: string, name: string) {
  if (!confirm(`确认删除项目「${name}」？`)) return
  await removeProject(id)
}

async function handleSync(id: string) {
  syncing.value[id] = true
  const result = await sync(id)
  syncing.value[id] = false
  if (result) {
    syncResults.value[id] = { ...result, ts: Date.now() }
    setTimeout(() => { delete syncResults.value[id] }, 5000)
  }
}
</script>

<template>
  <div>
    <!-- Page header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="page-title">项目工作区</h1>
        <p class="page-subtitle">{{ projects.length }} 个项目</p>
      </div>
      <button class="btn-primary" @click="showModal = true">
        <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
          <path d="M6.5 1v11M1 6.5h11" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
        新增项目
      </button>
    </div>

    <!-- Error -->
    <div v-if="error" class="error-bar mb-6">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" class="shrink-0">
        <circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.3"/>
        <path d="M7 4v3M7 9.5v.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
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

    <!-- Empty -->
    <div v-else-if="projects.length === 0" class="empty-state">
      <div class="empty-icon">
        <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
          <rect x="2" y="2" width="7.5" height="7.5" rx="1.5" stroke="currentColor" stroke-width="1.4"/>
          <rect x="12.5" y="2" width="7.5" height="7.5" rx="1.5" stroke="currentColor" stroke-width="1.4"/>
          <rect x="2" y="12.5" width="7.5" height="7.5" rx="1.5" stroke="currentColor" stroke-width="1.4"/>
          <rect x="12.5" y="12.5" width="7.5" height="7.5" rx="1.5" stroke="currentColor" stroke-width="1.4"/>
        </svg>
      </div>
      <p class="empty-title">还没有项目</p>
      <p class="empty-desc">添加一个本地项目开始管理任务</p>
      <button class="btn-secondary mt-4" @click="showModal = true">新增项目</button>
    </div>

    <!-- Project grid -->
    <div v-else class="project-grid">
      <div
        v-for="project in projects"
        :key="project.id"
        class="project-card"
        @click="router.push(`/project/${project.id}`)"
      >
        <!-- Card top -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0 pr-3">
            <h3 class="card-title truncate">{{ project.name }}</h3>
            <p class="card-path mono truncate">{{ project.path }}</p>
          </div>
          <div class="flex items-center gap-0.5 shrink-0" @click.stop>
            <button
              class="icon-btn sync-btn"
              :class="{ spinning: syncing[project.id] }"
              title="同步任务清单"
              :disabled="syncing[project.id]"
              @click="handleSync(project.id)"
            >
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <path d="M11 6.5A4.5 4.5 0 1 1 8.5 2.4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
                <path d="M8.5 1v3h3" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <button class="icon-btn del-btn" title="删除项目" @click="handleDelete(project.id, project.name)">
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                <path d="M1.5 3h9M4.5 3V2a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 .5.5v1M5 5.5v3.5M7 5.5v3.5M2 3l.5 6.5a.5.5 0 0 0 .5.5h6a.5.5 0 0 0 .5-.5L10 3"
                      stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Sync result -->
        <div v-if="syncResults[project.id]" class="sync-result mb-3">
          <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
            <path d="M1.5 5.5l2.5 2.5L9.5 2" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          同步完成 · +{{ syncResults[project.id]?.added }} 新增 · {{ syncResults[project.id]?.unchanged }} 不变 · 共 {{ syncResults[project.id]?.total }}
        </div>

        <div class="divider mb-3"></div>

        <!-- Stats -->
        <div class="flex flex-wrap gap-1.5">
          <span class="stat stat-total">全部 {{ project.taskStats.total }}</span>
          <span v-if="project.taskStats.pending > 0" class="stat stat-pending">待开发 {{ project.taskStats.pending }}</span>
          <span v-if="project.taskStats.in_progress > 0" class="stat stat-progress">进行中 {{ project.taskStats.in_progress }}</span>
          <span v-if="project.taskStats.pending_review > 0" class="stat stat-review">待 review {{ project.taskStats.pending_review }}</span>
          <span v-if="project.taskStats.completed > 0" class="stat stat-done">已完成 {{ project.taskStats.completed }}</span>
          <span v-if="project.taskStats.failed > 0" class="stat stat-fail">失败 {{ project.taskStats.failed }}</span>
        </div>
      </div>
    </div>

    <!-- Add Project Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-backdrop" @click.self="showModal = false">
        <div class="modal-box">
          <div class="flex items-center justify-between mb-5">
            <h2 class="modal-title">新增项目</h2>
            <button class="icon-btn" @click="showModal = false">
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                <path d="M1.5 1.5l10 10M11.5 1.5l-10 10" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <div class="space-y-4">
            <div>
              <label class="field-label">项目名称</label>
              <input v-model="newName" type="text" placeholder="my-awesome-project"
                     class="field-input" @keyup.enter="handleAdd" />
            </div>
            <div>
              <label class="field-label">本地路径</label>
              <input v-model="newPath" type="text" placeholder="/path/to/project"
                     class="field-input mono" @keyup.enter="handleAdd" />
            </div>
          </div>
          <div class="flex gap-2 mt-6">
            <button
              class="btn-primary flex-1"
              :disabled="submitting || !newName.trim() || !newPath.trim()"
              @click="handleAdd"
            >
              {{ submitting ? '添加中…' : '添加项目' }}
            </button>
            <button class="btn-secondary" @click="showModal = false">取消</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600&family=JetBrains+Mono:wght@400;500&display=swap');

.mono { font-family: 'JetBrains Mono', monospace; }
.muted { color: #7d8590; }

.page-title { font-size: 1.375rem; font-weight: 600; color: #e6edf3; letter-spacing: -0.02em; }
.page-subtitle { font-size: 0.75rem; color: #7d8590; margin-top: 2px; font-family: 'JetBrains Mono', monospace; }

.btn-primary {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 14px; border-radius: 8px; font-size: 0.8125rem; font-weight: 500;
  background: #1f6feb; color: #fff; border: 1px solid rgba(56,139,253,0.25);
  cursor: pointer; transition: background 0.15s;
}
.btn-primary:hover:not(:disabled) { background: #388bfd; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secondary {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 14px; border-radius: 8px; font-size: 0.8125rem; font-weight: 500;
  background: #21262d; color: #8b949e; border: 1px solid #30363d;
  cursor: pointer; transition: background 0.15s;
}
.btn-secondary:hover { background: #2d333b; }

.error-bar {
  display: flex; align-items: center; gap: 8px; padding: 10px 14px; border-radius: 8px;
  background: #3d1c1c; border: 1px solid rgba(248,81,73,0.25); color: #ff7b72; font-size: 0.8125rem;
}

.spinner {
  width: 15px; height: 15px; border-radius: 50%;
  border: 2px solid #1f6feb; border-top-color: transparent;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 80px 0; text-align: center;
}
.empty-icon {
  width: 52px; height: 52px; border-radius: 12px; display: flex; align-items: center;
  justify-content: center; background: #161b22; border: 1px solid #30363d; color: #7d8590; margin-bottom: 14px;
}
.empty-title { font-weight: 500; color: #e6edf3; margin-bottom: 4px; }
.empty-desc { font-size: 0.8125rem; color: #7d8590; }

.project-grid { display: grid; gap: 14px; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }

.project-card {
  background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 18px;
  cursor: pointer; transition: border-color 0.15s, box-shadow 0.15s;
}
.project-card:hover {
  border-color: rgba(56,139,253,0.4);
  box-shadow: 0 0 0 1px rgba(56,139,253,0.08);
}

.card-title { font-size: 0.9375rem; font-weight: 600; color: #e6edf3; letter-spacing: -0.01em; }
.card-path { font-size: 0.6875rem; color: #7d8590; margin-top: 2px; }

.icon-btn {
  width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center;
  color: #7d8590; background: transparent; border: none; cursor: pointer; transition: color 0.15s, background 0.15s;
}
.icon-btn:hover { color: #c9d1d9; background: #21262d; }
.sync-btn:hover { color: #58a6ff; background: #1a2d45; }
.del-btn:hover { color: #ff7b72; background: #3d1c1c; }
.spinning svg { animation: spin 0.8s linear infinite; }

.sync-result {
  display: flex; align-items: center; gap: 6px; padding: 6px 10px; border-radius: 6px;
  background: #1a2d1a; border: 1px solid rgba(63,185,80,0.25); color: #3fb950;
  font-size: 0.6875rem; font-family: 'JetBrains Mono', monospace;
}

.divider { height: 1px; background: #21262d; }

.stat {
  font-size: 0.6875rem; padding: 2px 8px; border-radius: 20px;
  font-family: 'JetBrains Mono', monospace;
}
.stat-total   { background: #21262d; color: #7d8590; }
.stat-pending { background: #21262d; color: #8b949e; }
.stat-progress { background: #1a2d45; color: #58a6ff; }
.stat-review  { background: #2d2200; color: #d29922; }
.stat-done    { background: #1a2d1a; color: #3fb950; }
.stat-fail    { background: #3d1c1c; color: #ff7b72; }

.modal-backdrop {
  position: fixed; inset: 0; display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.65); backdrop-filter: blur(4px); z-index: 50; padding: 16px;
}
.modal-box {
  width: 100%; max-width: 420px; background: #161b22; border: 1px solid #30363d;
  border-radius: 14px; padding: 22px; box-shadow: 0 20px 48px rgba(0,0,0,0.5);
}
.modal-title { font-size: 1rem; font-weight: 600; color: #e6edf3; letter-spacing: -0.02em; }

.field-label { display: block; font-size: 0.75rem; font-weight: 500; color: #8b949e; margin-bottom: 6px; }
.field-input {
  width: 100%; padding: 9px 12px; border-radius: 8px; font-size: 0.8125rem; outline: none;
  background: #0d1117; border: 1px solid #30363d; color: #e6edf3; transition: border-color 0.15s;
  box-sizing: border-box;
}
.field-input:focus { border-color: #388bfd; }
.field-input::placeholder { color: #484f58; }
</style>
