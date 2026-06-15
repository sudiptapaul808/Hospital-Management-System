<script setup>
import AdminNavbar from '../components/admin/AdminNavbar.vue'
import AdminSidebar from '../components/admin/AdminSidebar.vue'
</script>

<template>
  <AdminSidebar />
  <AdminNavbar />

  <v-main>
    <v-container fluid>
      <router-view />
    </v-container>
  </v-main>
</template>