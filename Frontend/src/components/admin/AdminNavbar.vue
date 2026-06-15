<script setup>
import { useUserStore } from '../../stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <v-app-bar app color="surface">

    <v-toolbar-title>Admin Panel</v-toolbar-title>

    <v-spacer />

    <v-btn @click="logout" variant="tonal">Logout</v-btn>

  </v-app-bar>
</template>