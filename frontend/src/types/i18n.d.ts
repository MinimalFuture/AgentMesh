declare module 'vue-i18n' {
  import { ComponentCustomProperties } from 'vue'
  
  declare module '@vue/runtime-core' {
    interface ComponentCustomProperties {
      $t: (key: string) => string
    }
  }
}

export {} 