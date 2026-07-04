<script setup>
import { ref } from 'vue';
import api from '../services/api'
import { useUserStore } from '../stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')

const handleLogin = async () => {
    try {
        const res = await api.post('/api/login', {
            email: email.value,
            password: password.value
        })
        userStore.setUser(res.data)
        if (res.data.role === 'admin') {
            router.push('/admin')
        } else if (res.data.role === 'doctor') {
            router.push('/doctor')
        } else if (res.data.role === 'patient') {
            router.push('/patient')
        }
    } catch (err) {
        error.value = err.response?.data?.error || "Something went wrong"
    }
}

//Send the user to the registration page===================================================================
const goToRegister = () => {
    router.push('/register')
}
</script>
<template>
    <div>
        <h2>Login</h2>

        <input v-model="email" placeholder="Email" />
        <input v-model="password" type="password" placeholder="Password" />
        <p v-if="error">{{ error }}</p>
        <button @click="handleLogin">Login</button>
        <p>New Patient?</p>
        <button @click="goToRegister">Register</button>
    </div>
</template>