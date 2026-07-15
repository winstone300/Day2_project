<script setup>
import L from 'leaflet'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  places: { type: Array, required: true },
  category: { type: String, required: true },
})

const mapElement = ref(null)
let map = null
let markerLayer = null

function validPlaces() {
  return props.places.filter(
    (place) => Number.isFinite(place.latitude) && Number.isFinite(place.longitude),
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
  const places = validPlaces()
  const coordinates = []

  places.forEach((place, index) => {
    const coordinate = [place.latitude, place.longitude]
    coordinates.push(coordinate)
    const icon = L.divIcon({
      className: 'region-map-marker',
      html: `<span>${index + 1}</span>`,
      iconSize: [38, 46],
      iconAnchor: [19, 44],
      popupAnchor: [0, -40],
    })
    L.marker(coordinate, { icon, title: place.title })
      .bindPopup(popupContent(place), { maxWidth: 280 })
      .addTo(markerLayer)
  })

  if (!coordinates.length) {
    map.setView([37.5665, 126.978], 11)
  } else if (coordinates.length === 1) {
    map.setView(coordinates[0], 14)
  } else {
    map.fitBounds(coordinates, { padding: [36, 36], maxZoom: 14 })
  }
}

onMounted(async () => {
  await nextTick()
  map = L.map(mapElement.value, {
    scrollWheelZoom: false,
    zoomControl: true,
  }).setView([37.5665, 126.978], 11)

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map)

  markerLayer = L.layerGroup().addTo(map)
  renderMarkers()
  window.setTimeout(() => map?.invalidateSize(), 0)
})

watch(() => props.places, renderMarkers)

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
