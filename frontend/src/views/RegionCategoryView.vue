<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getRegionCategory } from '../api/region'
import PaginationControls from '../components/PaginationControls.vue'
import RegionMap from '../components/RegionMap.vue'

const route = useRoute()
const router = useRouter()
const data = ref(null)
const loading = ref(true)
const error = ref('')
const selectedPlace = ref(null)
const mapModalClose = ref(null)
let mapTrigger = null

const category = computed(() => String(route.params.category || ''))
const currentPage = computed(() => {
  const page = Number.parseInt(String(route.query.page || '1'), 10)
  return Number.isFinite(page) && page > 0 ? page : 1
})

function safeImageUrl(url) {
  return url?.startsWith('https://') ? url : ''
}

async function loadCategory() {
  loading.value = true
  error.value = ''
  try {
    data.value = await getRegionCategory(category.value, currentPage.value)
  } catch (requestError) {
    error.value = requestError.message
    data.value = null
  } finally {
    loading.value = false
  }
}

function changePage(page) {
  closeMap(false)
  router.push({
    name: 'region-category',
    params: { category: category.value },
    query: page === 1 ? {} : { page },
  })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function openMap(place, event) {
  mapTrigger = event.currentTarget
  selectedPlace.value = place
  document.body.classList.add('region-map-modal-open')
  await nextTick()
  mapModalClose.value?.focus()
}

async function closeMap(restoreFocus = true) {
  selectedPlace.value = null
  document.body.classList.remove('region-map-modal-open')
  if (restoreFocus && mapTrigger) {
    await nextTick()
    mapTrigger.focus()
  }
  mapTrigger = null
}

watch([category, currentPage], loadCategory, { immediate: true })
onBeforeUnmount(() => document.body.classList.remove('region-map-modal-open'))
</script>

<template>
  <section class="region-category-page">
    <RouterLink class="back-link" to="/">← 서울 정보 전체 보기</RouterLink>

    <div class="page-heading compact">
      <div>
        <p class="eyebrow">EXPLORE SEOUL</p>
        <h1>{{ category }}</h1>
        <p v-if="data">
          서울의 {{ category }} 정보 <strong>{{ data.total.toLocaleString() }}</strong>곳을 확인해 보세요.
        </p>
        <p v-else>서울의 {{ category }} 정보를 확인해 보세요.</p>
      </div>
      <span v-if="data" class="page-count">페이지당 10개</span>
    </div>

    <div v-if="loading" class="state-card">{{ category }} 정보를 불러오는 중입니다…</div>
    <div v-else-if="error" class="state-card error-state" role="alert">
      {{ error }}
      <button class="text-button" type="button" @click="loadCategory">다시 시도</button>
    </div>

    <template v-else-if="data">
      <div v-if="data.items.length" class="region-place-grid">
        <article
          v-for="(place, index) in data.items"
          :key="place.content_id"
          class="region-place-card card"
          role="button"
          tabindex="0"
          :aria-label="`${index + 1}번 ${place.title} 지도에서 보기`"
          @click="openMap(place, $event)"
          @keydown.enter="openMap(place, $event)"
          @keydown.space.prevent="openMap(place, $event)"
        >
          <img
            v-if="safeImageUrl(place.image_url)"
            :src="safeImageUrl(place.image_url)"
            :alt="`${place.title} 대표 이미지`"
            loading="lazy"
          />
          <div v-else class="region-place-fallback" aria-hidden="true">
            {{ category.slice(0, 1) }}
          </div>
          <div class="region-place-copy">
            <span><b>{{ index + 1 }}</b>{{ place.category }}</span>
            <h2>{{ place.title }}</h2>
            <p>{{ place.address || '주소 정보가 제공되지 않았습니다.' }}</p>
            <small v-if="place.telephone">{{ place.telephone }}</small>
          </div>
        </article>
      </div>
      <div v-else class="state-card empty-state">
        <strong>이 페이지에 표시할 정보가 없습니다.</strong>
      </div>

      <PaginationControls
        :page="data.page"
        :total-pages="data.total_pages"
        @change="changePage"
      />
    </template>

    <Teleport to="body">
      <div
        v-if="selectedPlace && data"
        class="modal-backdrop region-map-modal-backdrop"
        @click.self="closeMap()"
        @keydown.esc="closeMap()"
      >
        <section
          class="modal-card region-map-dialog"
          role="dialog"
          aria-modal="true"
          aria-labelledby="region-map-dialog-title"
        >
          <button
            ref="mapModalClose"
            class="modal-close"
            type="button"
            aria-label="지도 팝업 닫기"
            @click="closeMap()"
          >
            &times;
          </button>
          <header class="region-map-dialog-header">
            <p class="eyebrow">PLACE MAP</p>
            <h2 id="region-map-dialog-title">{{ selectedPlace.title }}</h2>
            <p>{{ selectedPlace.address || '주소 정보가 제공되지 않았습니다.' }}</p>
          </header>
          <RegionMap
            :places="data.items"
            :category="data.category"
            :selected-place-id="selectedPlace.content_id"
          />
        </section>
      </div>
    </Teleport>
  </section>
</template>
