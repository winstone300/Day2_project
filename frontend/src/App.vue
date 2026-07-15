<script setup>
import { onMounted, ref } from 'vue'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const apiStatus = ref('확인 중')
const isConnected = ref(false)

onMounted(async () => {
  try {
    const response = await fetch(`${apiBaseUrl}/api/health`)
    const data = await response.json()
    isConnected.value = response.ok && data.database === 'connected' && data.region_data === 'loaded'
    apiStatus.value = isConnected.value ? '서비스 정상' : '서비스 점검 필요'
  } catch {
    apiStatus.value = 'API 연결 안 됨'
  }
})
</script>

<template>
  <div class="app-shell">
    <header class="site-header">
      <RouterLink class="brand" to="/">LocalHub</RouterLink>
      <nav aria-label="주요 메뉴">
        <RouterLink to="/">홈</RouterLink>
        <RouterLink to="/posts">게시판</RouterLink>
        <RouterLink to="/posts/new">글쓰기</RouterLink>
      </nav>
      <span class="api-status" :class="{ connected: isConnected }">{{ apiStatus }}</span>
    </header>

    <main class="page-container">
      <RouterView />
    </main>

    <footer>
      <strong>LocalHub 서울</strong>
      <span>한국관광공사 TourAPI 4.0 · 공공누리 제3유형 데이터를 활용합니다.</span>
    </footer>
  </div>
</template>
