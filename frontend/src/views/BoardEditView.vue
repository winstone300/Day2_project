<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getPost, updatePost, verifyPostPassword } from '../api/posts'
import PostForm from '../components/PostForm.vue'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const editPassword = ref('')
const passwordInput = ref('')
const authorized = ref(false)
const loading = ref(true)
const submitting = ref(false)
const error = ref('')

onMounted(async () => {
  const navigationState = window.history.state || {}
  if (navigationState.editPassword) {
    editPassword.value = navigationState.editPassword
    authorized.value = true
  }
  if (navigationState.post) {
    post.value = navigationState.post
  }
  window.history.replaceState(
    { ...navigationState, editPassword: undefined, post: undefined },
    document.title,
  )

  if (!post.value) {
    try {
      post.value = await getPost(route.params.id)
    } catch (requestError) {
      error.value = requestError.message
    }
  }
  loading.value = false
})

async function verifyPassword() {
  submitting.value = true
  error.value = ''
  try {
    await verifyPostPassword(route.params.id, passwordInput.value)
    editPassword.value = passwordInput.value
    passwordInput.value = ''
    authorized.value = true
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    submitting.value = false
  }
}

async function submitEdit(payload) {
  submitting.value = true
  error.value = ''
  try {
    await updatePost(route.params.id, { ...payload, edit_password: editPassword.value })
    router.push({ name: 'post-detail', params: { id: route.params.id } })
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <section class="form-page">
    <div class="page-heading compact">
      <div>
        <p class="eyebrow">EDIT STORY</p>
        <h1>게시글 수정</h1>
        <p>작성한 내용을 다듬어 다시 공유할 수 있습니다.</p>
      </div>
    </div>

    <div v-if="loading" class="state-card">게시글을 불러오는 중입니다…</div>
    <div v-else-if="!post" class="state-card error-state">{{ error }}</div>
    <form v-else-if="!authorized" class="password-gate card" @submit.prevent="verifyPassword">
      <p class="eyebrow">본인 확인</p>
      <h2>수정용 비밀번호를 입력해 주세요.</h2>
      <p>게시글 작성 시 등록한 비밀번호가 필요합니다.</p>
      <input
        v-model="passwordInput"
        type="password"
        required
        maxlength="100"
        autocomplete="current-password"
        placeholder="수정용 비밀번호"
      />
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <div class="form-actions">
        <button class="button secondary" type="button" @click="router.push(`/posts/${route.params.id}`)">
          취소
        </button>
        <button class="button primary" type="submit" :disabled="submitting">
          {{ submitting ? '확인 중…' : '비밀번호 확인' }}
        </button>
      </div>
    </form>
    <PostForm
      v-else
      mode="edit"
      :initial-post="post"
      :submitting="submitting"
      :error="error"
      @submit="submitEdit"
      @cancel="router.push(`/posts/${route.params.id}`)"
    />
  </section>
</template>
