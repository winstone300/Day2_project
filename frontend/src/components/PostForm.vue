<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  mode: { type: String, default: 'create' },
  initialPost: { type: Object, default: null },
  submitting: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['submit', 'cancel'])

const form = reactive({
  title: '',
  content: '',
  edit_password: '',
})

watch(
  () => props.initialPost,
  (post) => {
    if (!post) return
    form.title = post.title || ''
    form.content = post.content || ''
  },
  { immediate: true },
)

function submitForm() {
  emit('submit', {
    title: form.title,
    content: form.content,
    ...(props.mode === 'create' ? { edit_password: form.edit_password } : {}),
  })
}
</script>

<template>
  <form class="post-form card" @submit.prevent="submitForm">
    <div class="field-group">
      <div class="field-heading">
        <label for="post-title">제목</label>
        <span>{{ form.title.length }}/200</span>
      </div>
      <input
        id="post-title"
        v-model="form.title"
        maxlength="200"
        required
        autocomplete="off"
        placeholder="공유할 이야기의 제목을 입력해 주세요"
      />
    </div>

    <div class="field-group">
      <div class="field-heading">
        <label for="post-content">내용</label>
        <span>{{ form.content.length }}/10,000</span>
      </div>
      <textarea
        id="post-content"
        v-model="form.content"
        maxlength="10000"
        required
        rows="13"
        placeholder="서울에 관한 경험과 정보를 자유롭게 공유해 주세요"
      />
    </div>

    <div v-if="mode === 'create'" class="field-group password-field">
      <label for="post-password">수정용 비밀번호</label>
      <input
        id="post-password"
        v-model="form.edit_password"
        type="password"
        maxlength="100"
        required
        autocomplete="new-password"
        placeholder="수정·삭제할 때 사용할 비밀번호"
      />
      <p class="field-help">회원가입 없이 글을 관리할 때 사용합니다. 비밀번호를 기억해 주세요.</p>
    </div>

    <p v-if="error" class="form-error" role="alert">{{ error }}</p>

    <div class="form-actions">
      <button class="button secondary" type="button" :disabled="submitting" @click="$emit('cancel')">
        취소
      </button>
      <button class="button primary" type="submit" :disabled="submitting">
        {{ submitting ? '저장 중…' : mode === 'create' ? '게시글 등록' : '수정 완료' }}
      </button>
    </div>
  </form>
</template>
