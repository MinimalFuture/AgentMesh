<template>
  <div
    class="flex-1 flex items-center justify-center text-center p-5 min-h-[calc(100vh-140px)]"
  >
    <div class="w-full max-w-4xl flex flex-col items-center gap-10">
      <div class="text-center">
        <h1
          class="text-5xl font-bold bg-gradient-to-br from-primary-500 via-primary-800 to-blue-500 bg-clip-text text-transparent mb-4 leading-tight tracking-tight drop-shadow-lg"
        >
          {{ $t("welcome.title") }}
        </h1>
        <p class="text-lg text-gray-500 m-0 font-normal">
          {{ $t("welcome.subtitle") }}
        </p>
      </div>

      <!-- Centered Input Area -->
      <div class="w-full max-w-4xl">
        <div
          class="flex items-start bg-white/95 border border-white/30 rounded-2xl px-7 py-6 backdrop-blur-xl shadow-lg transition-all duration-300 ease-in-out min-h-50"
        >
          <textarea
            :value="inputMessage"
            @input="(event) => $emit('update:inputMessage', (event.target as HTMLTextAreaElement).value)"
            @keydown="handleKeyDown"
            :placeholder="$t('welcome.placeholder')"
            class="flex-1 border-none outline-none resize-none text-lg leading-relaxed font-inherit min-h-35 max-h-35 bg-transparent text-gray-700 align-top"
            rows="1"
            ref="chatInput"
          ></textarea>
          <div class="flex items-end gap-2 ml-3 self-end">
            <button
              class="bg-transparent border-none cursor-pointer p-2 rounded-lg text-gray-400 transition-all duration-200 ease-in-out flex items-center justify-center hover:bg-primary-500/10 hover:text-primary-500"
              :title="$t('welcome.uploadFile')"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66L9.64 16.2a2 2 0 0 1-2.83-2.83l8.49-8.49"
                />
              </svg>
            </button>
            <button
              class="bg-transparent border-none cursor-pointer p-2 rounded-lg text-gray-400 transition-all duration-200 ease-in-out flex items-center justify-center hover:bg-primary-500/10 hover:text-primary-500"
              :title="$t('welcome.voiceInput')"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path
                  d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"
                />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <path d="M12 19v3" />
              </svg>
            </button>
            <button
              class="bg-transparent border-none cursor-pointer p-2 rounded-lg text-gray-400 transition-all duration-200 ease-in-out flex items-center justify-center hover:bg-primary-500/10 hover:text-primary-500"
              :title="$t('welcome.moreOptions')"
            >
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <circle cx="12" cy="12" r="1" />
                <circle cx="19" cy="12" r="1" />
                <circle cx="5" cy="12" r="1" />
              </svg>
            </button>
            <button
              @click="$emit('send')"
              :disabled="!inputMessage.trim() || isLoading"
              class="bg-gradient-to-br from-primary-500 to-primary-800 text-white border-none rounded-xl p-2.5 cursor-pointer transition-all duration-300 ease-in-out flex items-center justify-center min-w-10 h-10 shadow-lg hover:from-primary-800 hover:to-primary-900 hover:-translate-y-0.5 hover:shadow-xl disabled:bg-gray-300 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
            >
              <svg
                v-if="!isLoading"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M22 2L11 13" />
                <path d="M22 2L15 22L11 13L2 9L22 2Z" />
              </svg>
              <div
                v-else
                class="w-4 h-4 border-2 border-transparent border-t-white rounded-full animate-spin"
              ></div>
            </button>
          </div>
        </div>
      </div>

      <!-- Example prompts below input -->
      <div class="grid grid-cols-2 gap-3 w-full max-w-4xl">
        <button
          v-for="example in examplePrompts"
          :key="example"
          class="flex items-center gap-2 p-4 bg-white/80 border border-white/30 rounded-xl cursor-pointer transition-all duration-300 ease-in-out text-left text-sm text-gray-700 backdrop-blur-md hover:bg-white/95 hover:-translate-y-0.5 hover:shadow-xl"
          @click="$emit('setInputValue', example)"
        >
          <span class="text-base">💡</span>
          {{ example }}
        </button>
      </div>

      <!-- i18n Test Component (for development) -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, withDefaults, computed } from "vue";
import { useI18n } from "vue-i18n";
import type { WelcomeSectionProps, WelcomeSectionEmits } from "../types";

const { t } = useI18n();

const props = withDefaults(defineProps<WelcomeSectionProps>(), {
  inputMessage: "",
  isLoading: false,
});

const emit = defineEmits<WelcomeSectionEmits>();

const examplePrompts = computed(() => [
  t("welcome.examplePrompts.businessReport"),
  t("welcome.examplePrompts.webScraper"),
  t("welcome.examplePrompts.dashboard"),
  t("welcome.examplePrompts.apiDocs"),
]);

const handleKeyDown = (event: KeyboardEvent): void => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    emit("send");
  }
};
</script>

<style scoped>
/* Focus styles */
.backdrop-blur-xl:focus-within {
  @apply border-primary-500 shadow-xl -translate-y-0.5;
}

/* Responsive */
@media (max-width: 768px) {
  .text-5xl {
    font-size: 2.25rem;
  }

  .text-lg {
    font-size: 1rem;
  }

  .grid-cols-2 {
    grid-template-columns: 1fr;
  }

  .min-h-50 {
    min-height: 10rem;
    align-items: flex-start;
  }

  .min-h-35 {
    min-height: 6.25rem;
    max-height: 6.25rem;
  }

  .text-lg {
    font-size: 1rem;
  }
}
</style>
