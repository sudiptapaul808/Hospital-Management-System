<script setup>
import DoctorNavbar from '../components/doctor/DoctorNavbar.vue';
import DoctorSidebar from '../components/doctor/DoctorSidebar.vue';
</script>

<template>
    <DoctorSidebar />
    <DoctorNavbar />

    <v-main>
        <v-container fluid>
            <router-view />
        </v-container>
    </v-main>
</template>