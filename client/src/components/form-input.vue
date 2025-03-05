<script setup lang="ts">
interface FormInputProps {
  modelValue: string
  id: string
  label?: string
  type?: string
  placeholder?: string
  icon?: string
  size?: 'sm' | 'md' | 'lg'
}

withDefaults(defineProps<FormInputProps>(), {
  type: 'text',
  size: 'md'
})

const emit = defineEmits(['update:modelValue'])

const inputSize = {
  'sm': 'px-2 py-1 h-[28px]',
  'md': 'px-3 py-1.5 h-[36px]',
  'lg': 'px-4 py-2 h-[46px]',
}

const handleInput = (event: Event) => {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <div class="space-y-1">
    <label :for="id" class="text-slate-500">{{ label }}</label>
    <div class="relative">
      <input
        :id="id"
        class="w-full border border-gray-200 rounded-lg focus:outline-teal-500 peer"
        :class="[
          icon ? 'pl-8' : '',
          inputSize[size]
        ]"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        @input="handleInput"
      >
      <font-awesome-icon
        v-if="icon"
        class="absolute left-2.5 top-2.5 text-slate-500 peer-focus:text-teal-500"
        :icon="['fas', icon]"
      />
    </div>
  </div>
</template>