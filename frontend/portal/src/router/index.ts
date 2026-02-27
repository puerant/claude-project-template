import { createRouter, createWebHistory } from 'vue-router'
import ProjectList from '../views/ProjectList.vue'
import ProjectBoard from '../views/ProjectBoard.vue'
import TaskDetail from '../views/TaskDetail.vue'
import LogView from '../views/LogView.vue'
import BugList from '../views/BugList.vue'

const routes = [
  { path: '/', component: ProjectList },
  { path: '/project/:id', component: ProjectBoard },
  { path: '/project/:id/task/:taskId', component: TaskDetail },
  { path: '/project/:id/task/:taskId/log', component: LogView },
  { path: '/project/:id/bugs', component: BugList },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
