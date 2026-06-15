<script setup>
import { onMounted } from 'vue'
import api from '../../services/api'
import { useUserStore } from '../../stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

onMounted(async () => {
    try {
        const res = await api.get('/api/admin_dashboard/summary')
        console.log(res.data)
    } catch (err) {
        console.log(err)
    }
})

const handleLogout = () => {
    userStore.logout()
    router.push('/login')
}
</script>

<template>
    <h1>Admin Summary Page</h1>
    <button @click="handleLogout">Logout</button>
</template>