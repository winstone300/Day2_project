<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { createPost } from '../api/posts'
import PostForm from '../components/PostForm.vue'

const router = useRouter()
const submitting = ref(false)
const error = ref('')

async function submitPost(payload) {
  submitting.value = true
  error.value = ''
  try {
    const created = await createPost(payload)
    router.push({ name: 'post-detail', params: { id: created.id } })
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
        <p class="eyebrow">NEW STORY</p>
        <h1>새 이야기 작성</h1>
        <p>서울에서 발견한 장소와 경험을 이웃과 나눠 주세요.</p>
      </div>
    </div>
    <PostForm
      mode="create"
      :submitting="submitting"
      :error="error"
      @submit="submitPost"
      @cancel="router.push('/posts')"
    />
  </section>
</template>
