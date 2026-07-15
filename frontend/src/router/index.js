import { createRouter, createWebHistory } from 'vue-router'

import BoardCreateView from '../views/BoardCreateView.vue'
import BoardDetailView from '../views/BoardDetailView.vue'
import BoardEditView from '../views/BoardEditView.vue'
import BoardListView from '../views/BoardListView.vue'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/posts', name: 'posts', component: BoardListView },
    { path: '/posts/new', name: 'post-create', component: BoardCreateView },
    { path: '/posts/:id', name: 'post-detail', component: BoardDetailView },
    { path: '/posts/:id/edit', name: 'post-edit', component: BoardEditView },
  ],
})

export default router
