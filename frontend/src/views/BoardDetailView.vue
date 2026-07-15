<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { deletePost, getPost, verifyPostPassword } from '../api/posts'
import PasswordModal from '../components/PasswordModal.vue'
import { formatDateTime } from '../utils/date'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const loading = ref(true)
const error = ref('')
const modal = reactive({ open: false, action: 'edit', loading: false, error: '' })

async function loadPost() {
  loading.value = true
  error.value = ''
  try {
    post.value = await getPost(route.params.id)
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
  }
}

function openPasswordModal(action) {
  modal.action = action
  modal.error = ''
  modal.open = true
}

async function confirmPassword(password) {
  modal.loading = true
  modal.error = ''
  try {
    if (modal.action === 'edit') {
      await verifyPostPassword(post.value.id, password)
      router.push({
        name: 'post-edit',
        params: { id: post.value.id },
        state: { editPassword: password, post: { title: post.value.title, content: post.value.content } },
      })
      return
    }

    await deletePost(post.value.id, password)
    router.push('/posts')
  } catch (requestError) {
    modal.error = requestError.message
  } finally {
    modal.loading = false
  }
}

onMounted(loadPost)
</script>

<template>
  <section class="detail-page">
    <RouterLink class="back-link" to="/posts">← 목록으로 돌아가기</RouterLink>

    <div v-if="loading" class="state-card">게시글을 불러오는 중입니다…</div>
    <div v-else-if="error" class="state-card error-state" role="alert">
      {{ error }}
      <RouterLink class="text-link" to="/posts">게시판으로 이동</RouterLink>
    </div>
    <article v-else class="post-detail card">
      <header>
        <p class="eyebrow">SEOUL STORY</p>
        <h1>{{ post.title }}</h1>
        <div class="post-meta">
          <span>{{ formatDateTime(post.created_at) }}</span>
          <span>조회 {{ post.view_count.toLocaleString() }}</span>
        </div>
      </header>
      <div class="post-content">{{ post.content }}</div>
      <footer class="detail-actions">
        <button class="button secondary" type="button" @click="openPasswordModal('edit')">수정</button>
        <button class="button danger" type="button" @click="openPasswordModal('delete')">삭제</button>
      </footer>
    </article>

    <PasswordModal
      :open="modal.open"
      :title="modal.action === 'edit' ? '게시글을 수정할까요?' : '게시글을 삭제할까요?'"
      :description="
        modal.action === 'edit'
          ? '작성할 때 등록한 수정용 비밀번호를 확인합니다.'
          : '삭제한 게시글은 복구할 수 없습니다.'
      "
      :confirm-label="modal.action === 'edit' ? '수정 화면으로' : '게시글 삭제'"
      :loading="modal.loading"
      :error="modal.error"
      @close="modal.open = false"
      @confirm="confirmPassword"
    />
  </section>
</template>
