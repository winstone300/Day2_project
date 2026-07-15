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
let markerLayer = null
const markersById = new Map()

function validPlaces() {
  return props.places
    .map((place, index) => ({ place, number: index + 1 }))
    .filter(
      ({ place }) => Number.isFinite(place.latitude) && Number.isFinite(place.longitude),
    )
}

function popupContent(place) {
  const container = document.createElement('div')
  container.className = 'region-map-popup'

  const type = document.createElement('span')
  type.textContent = place.category
  const title = document.createElement('strong')
  title.textContent = place.title
  const address = document.createElement('p')
  address.textContent = place.address || '주소 정보가 제공되지 않았습니다.'

  container.append(type, title, address)
  return container
}

function renderMarkers() {
  if (!map || !markerLayer) return

  markerLayer.clearLayers()
  markersById.clear()
  const places = validPlaces()
  const coordinates = []

  places.forEach(({ place, number }) => {
    const coordinate = [place.latitude, place.longitude]
    coordinates.push(coordinate)
    const icon = L.divIcon({
      className: 'region-map-marker',
      html: `<span>${number}</span>`,
      iconSize: [38, 46],
      iconAnchor: [19, 44],
      popupAnchor: [0, -40],
    })
    const marker = L.marker(coordinate, { icon, title: place.title })
      .bindPopup(popupContent(place), { maxWidth: 280 })
      .addTo(markerLayer)
    markersById.set(String(place.content_id), marker)
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
  const marker = markersById.get(String(contentId))
  if (!map || !marker) return false

  const coordinate = marker.getLatLng()
  map.flyTo(coordinate, 16, { duration: 0.8 })
  marker.openPopup()
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

  markerLayer = L.layerGroup().addTo(map)
  renderMarkers()
  if (props.selectedPlaceId != null) {
    focusPlace(props.selectedPlaceId, false)
  }
  window.setTimeout(() => map?.invalidateSize(), 0)
})

watch(() => props.places, renderMarkers)
watch(() => props.selectedPlaceId, (contentId) => {
  if (contentId != null) focusPlace(contentId, false)
})

onBeforeUnmount(() => {
  map?.remove()
  map = null
  markerLayer = null
})
</script>

<template>
  <section class="region-map-section" aria-labelledby="region-map-title">
    <div class="section-heading">
      <div>
        <p class="eyebrow">MAP VIEW</p>
        <h2 id="region-map-title">지도에서 {{ category }} 보기</h2>
      </div>
      <span>현재 페이지 {{ validPlaces().length }}개 핀</span>
    </div>
    <div
      ref="mapElement"
      class="region-map-shell card"
      role="application"
      :aria-label="`서울 ${category} 위치 지도`"
    ></div>
  </section>
</template>
