<script setup>
import { onMounted } from 'vue'
import api from '../services/api'

onMounted(async () => {
  try {
    const res = await api.get('/api/admin_dashboard/summary')
    console.log(res.data)
  } catch (err) {
    console.log(err)
  }
})

import { useUserStore } from '../stores/user'

const userStore = useUserStore()

console.log("Token:", userStore.token)
console.log("Role:", userStore.user?.role)
</script>

<template>
  <h1>Home Page</h1>
</template>