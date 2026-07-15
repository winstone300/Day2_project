<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { sendChatMessage } from '../api/chat'

const suggestions = [
  '서울 축제 추천해줘',
  '강남 문화시설 알려줘',
  '최근 커뮤니티 글 보여줘',
]

const isOpen = ref(false)
const input = ref('')
const isSending = ref(false)
const inputElement = ref(null)
const messageList = ref(null)
let messageId = 1

const messages = ref([
  {
    id: messageId++,
    role: 'assistant',
    text: '안녕하세요! 서울의 장소를 추천하거나 LocalHub 커뮤니티 게시글을 찾아드릴게요.',
    places: [],
    posts: [],
    source: '',
  },
])

async function scrollToLatest() {
  await nextTick()
  if (messageList.value) {
    messageList.value.scrollTop = messageList.value.scrollHeight
  }
}

async function openChat() {
  isOpen.value = true
  await nextTick()
  inputElement.value?.focus()
  scrollToLatest()
}

function closeChat() {
  isOpen.value = false
}

function safeImageUrl(url) {
  return url?.startsWith('https://') ? url : ''
}

function displayMessage(message) {
  if (message.places.length) return message.text.split('\n')[0]
  return message.text
}

async function submitMessage(message = input.value) {
  const question = message.trim()
  if (!question || isSending.value) return

  messages.value.push({
    id: messageId++,
    role: 'user',
    text: question,
    places: [],
    posts: [],
    source: '',
  })
  input.value = ''
  isSending.value = true
  await scrollToLatest()

  try {
    const response = await sendChatMessage(question)
    messages.value.push({
      id: messageId++,
      role: 'assistant',
      text: response.answer,
      places: response.results || [],
      posts: response.post_results || [],
      source: response.source || '',
    })
  } catch (error) {
    messages.value.push({
      id: messageId++,
      role: 'assistant',
      text: error.message || '답변을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.',
      places: [],
      posts: [],
      source: '',
      error: true,
    })
  } finally {
    isSending.value = false
    await scrollToLatest()
    inputElement.value?.focus()
  }
}

function handleEscape(event) {
  if (event.key === 'Escape' && isOpen.value) closeChat()
}

watch(isOpen, (open) => {
  document.body.classList.toggle('chat-open', open)
})

onMounted(() => window.addEventListener('keydown', handleEscape))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleEscape)
  document.body.classList.remove('chat-open')
})
</script>

<template>
  <button
    v-if="!isOpen"
    class="chat-fab"
    type="button"
    aria-label="서울 도우미 챗봇 열기"
    @click="openChat"
  >
    <span class="chat-fab-icon" aria-hidden="true">AI</span>
    <span>서울 도우미</span>
  </button>

  <Transition name="chat-panel">
    <section
      v-if="isOpen"
      class="chat-window"
      role="dialog"
      aria-modal="true"
      aria-labelledby="chat-title"
    >
      <header class="chat-header">
        <div class="chat-avatar" aria-hidden="true">L</div>
        <div>
          <strong id="chat-title">LocalHub 서울 도우미</strong>
          <span><i aria-hidden="true"></i> 서울 데이터 연결됨</span>
        </div>
        <button type="button" aria-label="챗봇 닫기" @click="closeChat">×</button>
      </header>

      <div ref="messageList" class="chat-messages" aria-live="polite">
        <div
          v-for="message in messages"
          :key="message.id"
          class="chat-message-row"
          :class="message.role"
        >
          <div class="chat-bubble" :class="{ error: message.error }">
            <p>{{ displayMessage(message) }}</p>

            <div v-if="message.places.length" class="chat-results">
              <article v-for="place in message.places" :key="place.content_id" class="chat-place-card">
                <img
                  v-if="safeImageUrl(place.image_url)"
                  :src="safeImageUrl(place.image_url)"
                  :alt="`${place.title} 대표 이미지`"
                />
                <span v-else class="chat-result-fallback" aria-hidden="true">
                  {{ place.category.slice(0, 1) }}
                </span>
                <div>
                  <span class="chat-result-type">{{ place.category }}</span>
                  <strong>{{ place.title }}</strong>
                  <small>{{ place.address || '주소 정보 없음' }}</small>
                </div>
              </article>
            </div>

            <div v-if="message.posts.length" class="chat-results">
              <RouterLink
                v-for="post in message.posts"
                :key="post.id"
                class="chat-post-card"
                :to="`/posts/${post.id}`"
                @click="closeChat"
              >
                <span>커뮤니티</span>
                <strong>{{ post.title }}</strong>
                <small>{{ post.content_preview }}</small>
                <em>조회 {{ post.view_count.toLocaleString() }} · 게시글 보기 →</em>
              </RouterLink>
            </div>

            <small v-if="message.source" class="chat-source">출처: {{ message.source }}</small>
          </div>
        </div>

        <div v-if="messages.length === 1" class="chat-suggestions">
          <span>이렇게 물어보세요</span>
          <button
            v-for="suggestion in suggestions"
            :key="suggestion"
            type="button"
            @click="submitMessage(suggestion)"
          >
            {{ suggestion }}
          </button>
        </div>

        <div v-if="isSending" class="chat-message-row assistant">
          <div class="chat-bubble chat-typing" aria-label="답변 작성 중">
            <i></i><i></i><i></i>
          </div>
        </div>
      </div>

      <form class="chat-composer" @submit.prevent="submitMessage()">
        <label class="sr-only" for="chat-input">서울 정보 또는 게시글 질문</label>
        <input
          id="chat-input"
          ref="inputElement"
          v-model="input"
          maxlength="500"
          autocomplete="off"
          placeholder="서울 정보나 게시글을 물어보세요"
          :disabled="isSending"
        />
        <button type="submit" :disabled="!input.trim() || isSending" aria-label="메시지 보내기">
          <span aria-hidden="true">↑</span>
        </button>
      </form>
    </section>
  </Transition>
</template>
