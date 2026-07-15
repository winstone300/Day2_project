<script setup>
defineProps({
  page: { type: Number, required: true },
  totalPages: { type: Number, required: true },
})

defineEmits(['change'])
</script>

<template>
  <nav v-if="totalPages > 1" class="pagination" aria-label="페이지 이동">
    <button
      type="button"
      class="page-button"
      :disabled="page <= 1"
      aria-label="이전 페이지"
      @click="$emit('change', page - 1)"
    >
      ‹
    </button>
    <span><strong>{{ page }}</strong> / {{ totalPages }}</span>
    <button
      type="button"
      class="page-button"
      :disabled="page >= totalPages"
      aria-label="다음 페이지"
      @click="$emit('change', page + 1)"
    >
      ›
    </button>
  </nav>
</template>
