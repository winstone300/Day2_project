<script setup>
import { onMounted, ref } from 'vue'

import { getPosts } from '../api/posts'
import { getRegionSummary } from '../api/region'
import { formatDate } from '../utils/date'

const summary = ref(null)
const recentPosts = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const [regionData, postData] = await Promise.all([
      getRegionSummary(),
      getPosts({ page: 1, size: 5, sort: 'latest' }),
    ])
    summary.value = regionData
    recentPosts.value = postData.items
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="home-page">
    <section class="hero-card">
      <div>
        <p class="eyebrow">서울을 더 가까이, 이야기를 더 자유롭게</p>
        <h1>우리의 서울을<br />함께 발견해요.</h1>
        <p class="hero-copy">
          관광지부터 숙박, 문화시설까지 공공데이터로 살펴보고 익명 커뮤니티에서
          나만의 지역 경험을 나눠 보세요.
        </p>
        <div class="hero-actions">
          <RouterLink class="button primary" to="/posts">커뮤니티 둘러보기</RouterLink>
          <RouterLink class="button ghost" to="/posts/new">내 이야기 쓰기</RouterLink>
        </div>
      </div>
      <div class="hero-stat" aria-label="서울 데이터 수">
        <span>SEOUL DATA</span>
        <strong>{{ summary?.total?.toLocaleString() || '6,518' }}</strong>
        <small>개의 장소와 지역 정보</small>
      </div>
    </section>

    <div v-if="loading" class="state-card">서울 정보를 불러오는 중입니다…</div>
    <div v-else-if="error" class="state-card error-state" role="alert">{{ error }}</div>

    <template v-else>
      <section class="section-block">
        <div class="section-heading">
          <div>
            <p class="eyebrow">EXPLORE SEOUL</p>
            <h2>서울 정보 한눈에 보기</h2>
          </div>
          <span>{{ summary.categories.length }}개 카테고리</span>
        </div>
        <div class="category-grid">
          <RouterLink
            v-for="category in summary.categories"
            :key="category.name"
            class="category-card"
            :to="{ name: 'region-category', params: { category: category.name } }"
          >
            <span class="category-icon">{{ category.name.slice(0, 1) }}</span>
            <div>
              <h3>{{ category.name }}</h3>
              <p>{{ category.count.toLocaleString() }}곳</p>
            </div>
            <span class="category-arrow" aria-hidden="true">→</span>
          </RouterLink>
        </div>
      </section>

      <section class="section-block">
        <div class="section-heading">
          <div>
            <p class="eyebrow">LOCAL STORIES</p>
            <h2>최근 올라온 이야기</h2>
          </div>
          <RouterLink class="text-link" to="/posts">전체 게시글 보기 →</RouterLink>
        </div>
        <div v-if="recentPosts.length" class="recent-list card">
          <RouterLink
            v-for="post in recentPosts"
            :key="post.id"
            class="recent-row"
            :to="`/posts/${post.id}`"
          >
            <strong>{{ post.title }}</strong>
            <span>조회 {{ post.view_count.toLocaleString() }}</span>
            <time>{{ formatDate(post.created_at) }}</time>
          </RouterLink>
        </div>
        <div v-else class="state-card">첫 번째 서울 이야기를 남겨 보세요.</div>
      </section>
    </template>
  </div>
</template>
