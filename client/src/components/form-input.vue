<script setup lang="ts">
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
}

withDefaults(defineProps<FormInputProps>(), {
  type: 'text',
  size: 'md',
  iconPosition: 'prepend'
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
    <label :for="id" class="text-slate-500 text-sm">
      {{ label }} <sup v-if="required" class="text-red-500 font-semibold">*</sup>
    </label>
    <div class="relative">
      <div class="absolute left-2.5 top-2.5 flex justify-center items-center text-slate-500">
        <slot name="prepend-icon">
          <font-awesome-icon
            v-if="icon && iconPosition === 'prepend'"
            class="transition-colors duration-300"
            :class="error ? '!text-red-500' : 'peer-focus:!text-teal-500'"
            :icon="['fas', icon]"
          />
        </slot>
      </div>
      <div class="absolute right-2.5 top-2.5 flex justify-center items-center text-slate-500">
        <slot name="append-icon">
          <font-awesome-icon
            v-if="icon && iconPosition === 'append'"
            class="transition-colors duration-300"
            :class="error ? '!text-red-500' : 'peer-focus:!text-teal-500'"
            :icon="['fas', icon]"
          />
        </slot>
      </div>
      <input
        :id="id"
        class="w-full border rounded-lg peer transition-colors duration-300"
        :class="[
          icon ? 'pl-8' : '',
          inputSize[size],
          error ? 'border-red-500 outline-red-500' : 'focus:outline-teal-500 border-gray-200'
        ]"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        @input="handleInput"
      >
    </div>
    <p v-if="error && errorMessage" class="text-sm text-red-500">{{ errorMessage }}</p>
  </div>
</template>