<script setup>
import L from 'leaflet'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  places: { type: Array, required: true },
  category: { type: String, required: true },
  selectedPlaceId: { type: [String, Number], default: null },
})

const mapElement = ref(null)
let map = null

function validPlaces() {
  return props.places
    .filter((place) => Number.isFinite(place.latitude) && Number.isFinite(place.longitude))
}

function showPlaces() {
  if (!map) return

  const places = validPlaces()
  const coordinates = []

  places.forEach((place) => {
    const coordinate = [place.latitude, place.longitude]
    coordinates.push(coordinate)
  })

  if (!coordinates.length) {
    map.setView([37.5665, 126.978], 11)
  } else if (coordinates.length === 1) {
    map.setView(coordinates[0], 14)
  } else {
    map.fitBounds(coordinates, { padding: [36, 36], maxZoom: 14 })
  }
}

function focusPlace(contentId, scrollIntoView = true) {
  const selected = validPlaces().find(
    (place) => String(place.content_id) === String(contentId),
  )
  if (!map || !selected) return false

  const coordinate = [selected.latitude, selected.longitude]
  map.flyTo(coordinate, 16, { duration: 0.8 })
  if (scrollIntoView) {
    mapElement.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
  return true
}

defineExpose({ focusPlace })

onMounted(async () => {
  await nextTick()
  map = L.map(mapElement.value, {
    scrollWheelZoom: true,
    zoomControl: true,
  }).setView([37.5665, 126.978], 11)

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map)

  showPlaces()
  if (props.selectedPlaceId != null) {
    focusPlace(props.selectedPlaceId, false)
  }
  window.setTimeout(() => map?.invalidateSize(), 0)
})

watch(() => props.places, showPlaces)
watch(() => props.selectedPlaceId, (contentId) => {
  if (contentId != null) focusPlace(contentId, false)
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
})
</script>

<template>
  <section class="region-map-section" aria-labelledby="region-map-title">
    <div class="section-heading">
      <div>
        <p class="eyebrow">MAP VIEW</p>
        <h2 id="region-map-title">지도에서 {{ category }} 보기</h2>
      </div>
      <span>선택한 장소 주변 지도</span>
    </div>
    <div
      ref="mapElement"
      class="region-map-shell card"
      role="application"
      :aria-label="`서울 ${category} 위치 지도`"
    ></div>
  </section>
</template>
