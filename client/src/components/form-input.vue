<script setup lang="ts">
interface FormInputProps {
  modelValue: string
  id: string
  label?: string
  type?: string
  placeholder?: string
  icon?: string
}

withDefaults(defineProps<FormInputProps>(), {
  type: 'text'
})

const emit = defineEmits(['update:modelValue'])

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
        class="w-full h-[36px] border border-gray-200 rounded-lg px-3 py-1.5 focus:outline-teal-500 peer"
        :class="icon ? 'pl-8' : ''"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        @input="handleInput"
      >
      <font-awesome-icon
        v-if="icon"
        class="absolute left-2 top-2 text-slate-500 peer-focus:text-teal-500"
        :icon="['fas', icon]"
      />
    </div>
  </div>
</template>