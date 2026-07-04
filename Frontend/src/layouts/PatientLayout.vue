<script setup>
import PatientSidebar from '../components/patient/PatientSidebar.vue';
import PatientNavbar from '../components/patient/PatientNavbar.vue';
</script>

<template>
    <PatientSidebar />
    <PatientNavbar />

    <v-main>
        <v-container fluid>
            <router-view />
        </v-container>
    </v-main>
</template>