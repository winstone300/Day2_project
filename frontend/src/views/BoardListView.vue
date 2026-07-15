<script setup>
import { onMounted, ref } from 'vue'

import { getPosts } from '../api/posts'
import PaginationControls from '../components/PaginationControls.vue'
import { formatDate } from '../utils/date'

const posts = ref([])
const page = ref(1)
const total = ref(0)
const totalPages = ref(0)
const searchInput = ref('')
const activeQuery = ref('')
const sort = ref('latest')
const loading = ref(true)
const error = ref('')

async function loadPosts() {
  loading.value = true
  error.value = ''
  try {
    const data = await getPosts({
      page: page.value,
      size: 10,
      query: activeQuery.value,
      sort: sort.value,
    })
    posts.value = data.items
    total.value = data.total
    totalPages.value = data.total_pages
  } catch (requestError) {
    error.value = requestError.message
  } finally {
    loading.value = false
  }
}

function searchPosts() {
  activeQuery.value = searchInput.value.trim()
  page.value = 1
  loadPosts()
}

function changeSort() {
  page.value = 1
  loadPosts()
}

function changePage(nextPage) {
  page.value = nextPage
  loadPosts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(loadPosts)
</script>

<template>
  <section class="board-page">
    <div class="page-heading">
      <div>
        <p class="eyebrow">SEOUL COMMUNITY</p>
        <h1>서울 이야기</h1>
        <p>회원가입 없이 서울의 경험과 정보를 자유롭게 나눠 보세요.</p>
      </div>
      <RouterLink class="button primary" to="/posts/new">새 글 작성</RouterLink>
    </div>

    <div class="board-toolbar card">
      <form class="search-form" role="search" @submit.prevent="searchPosts">
        <label class="sr-only" for="post-search">게시글 검색</label>
        <input id="post-search" v-model="searchInput" type="search" placeholder="제목과 내용에서 검색" />
        <button class="button dark" type="submit">검색</button>
      </form>
      <label class="sort-control">
        <span>정렬</span>
        <select v-model="sort" @change="changeSort">
          <option value="latest">최신순</option>
          <option value="views">조회수순</option>
        </select>
      </label>
    </div>

    <p v-if="activeQuery && !loading" class="result-summary">
      ‘{{ activeQuery }}’ 검색 결과 <strong>{{ total.toLocaleString() }}</strong>건
    </p>

    <div v-if="loading" class="state-card">게시글을 불러오는 중입니다…</div>
    <div v-else-if="error" class="state-card error-state" role="alert">
      {{ error }}
      <button class="text-button" type="button" @click="loadPosts">다시 시도</button>
    </div>
    <div v-else-if="posts.length" class="post-list card">
      <RouterLink v-for="post in posts" :key="post.id" class="post-row" :to="`/posts/${post.id}`">
        <span class="post-number">{{ post.id }}</span>
        <strong>{{ post.title }}</strong>
        <span class="post-views">조회 {{ post.view_count.toLocaleString() }}</span>
        <time>{{ formatDate(post.created_at) }}</time>
      </RouterLink>
    </div>
    <div v-else class="state-card empty-state">
      <strong>게시글을 찾지 못했습니다.</strong>
      <span>검색어를 바꾸거나 첫 번째 이야기를 작성해 보세요.</span>
    </div>

    <PaginationControls :page="page" :total-pages="totalPages" @change="changePage" />
  </section>
</template>
