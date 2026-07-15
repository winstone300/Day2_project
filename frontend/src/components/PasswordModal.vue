<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, required: true },
  description: { type: String, default: '' },
  confirmLabel: { type: String, default: '확인' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['close', 'confirm'])
const password = ref('')

watch(
  () => props.open,
  (open) => {
    if (open) password.value = ''
  },
)

function closeModal() {
  if (!props.loading) emit('close')
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="modal-backdrop" @click.self="closeModal">
      <form class="modal-card" role="dialog" aria-modal="true" @submit.prevent="$emit('confirm', password)">
        <button class="modal-close" type="button" aria-label="닫기" :disabled="loading" @click="closeModal">
          ×
        </button>
        <p class="eyebrow">본인 확인</p>
        <h2>{{ title }}</h2>
        <p class="modal-description">{{ description }}</p>
        <label for="modal-password">수정용 비밀번호</label>
        <input
          id="modal-password"
          v-model="password"
          type="password"
          required
          maxlength="100"
          autocomplete="current-password"
          autofocus
          placeholder="게시글 작성 시 입력한 비밀번호"
        />
        <p v-if="error" class="form-error" role="alert">{{ error }}</p>
        <div class="form-actions">
          <button class="button secondary" type="button" :disabled="loading" @click="closeModal">취소</button>
          <button class="button primary" type="submit" :disabled="loading">
            {{ loading ? '확인 중…' : confirmLabel }}
          </button>
        </div>
      </form>
    </div>
  </Teleport>
</template>
