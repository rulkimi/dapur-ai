<script setup lang="ts">
import { useSlots } from 'vue'

interface FormInputProps {
  modelValue: string
  id: string
  label?: string
  type?: string
  placeholder?: string
  icon?: string
  iconPosition?: 'append' | 'prepend'
  size?: 'sm' | 'md' | 'lg'
  error?: boolean
  errorMessage?: string
  required?: boolean
  readonly?: boolean
}

withDefaults(defineProps<FormInputProps>(), {
  type: 'text',
  size: 'md',
  iconPosition: 'prepend'
})

const emit = defineEmits(['update:modelValue'])
const slots = useSlots()
const hasAppendIcon = !!slots['append-icon']
const hasPrependIcon = !!slots['prepend-icon']

const inputSize = {
  'sm': 'px-2 py-1 h-[28px]',
  'md': 'px-3 py-1.5 h-[36px]',
  'lg': 'px-4 py-2 h-[46px]',
}

const inputClasses = {
  error : 'border-red-500 outline-red-500',
  focus: 'focus:outline-teal-500 border-gray-200',
  readonly: 'border-b focus:!outline-none pointer-events-none'
}

const handleInput = (event: Event) => {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <div class="space-y-1">
    <label :for="id" class="text-slate-500 text-sm">
      {{ label }} <sup v-if="required" class="text-red-500 font-semibold">*</sup>
    </label>
    <div class="relative peer">
      <input
        :id="readonly ? id : `${id}-readonly`"
        class="w-full peer transition-colors duration-300"
        :class="[
          icon ? 'pl-8' : '',
          inputSize[size],
          error ? inputClasses.error : inputClasses.focus,
          readonly ? inputClasses.readonly : 'border rounded-lg'
        ]"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        @input="handleInput"
      >
      <div
        v-if="(icon && iconPosition === 'prepend') || hasPrependIcon"
        class="absolute left-2.5 top-2.5 flex justify-center items-center"
        :class="error ? '!text-red-500' : 'peer-focus:!text-teal-500 text-slate-500'"
      >
        <slot name="prepend-icon">
          <font-awesome-icon
            class="transition-colors duration-300"
            :icon="['fas', icon]"
          />
        </slot>
      </div>
      <div
        v-if="(icon && iconPosition === 'append') || hasAppendIcon"
        class="absolute right-2.5 top-2.5 flex justify-center items-center"
        :class="error ? '!text-red-500' : 'peer-focus:!text-teal-500 text-slate-500'"
      >
        <slot name="append-icon">
          <font-awesome-icon
            class="transition-colors duration-300"
            :icon="['fas', icon]"
          />
        </slot>
      </div>
    </div>
    <p v-if="error && errorMessage" class="text-sm text-red-500">{{ errorMessage }}</p>
  </div>
</template>