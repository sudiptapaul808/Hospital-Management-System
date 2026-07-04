<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
</script>

<template>
    <v-navigation-drawer app permanent color="primary" dark>
        <v-list-item
        active-color="white"
        title="Dashboard"
        to="/patient"
        exact
        >
            <template #prepend>
                <v-icon>mdi-view-dashboard</v-icon>
            </template>
        </v-list-item>

        <v-list-item
        active-color="white"
        title="Upcoming Appointments"
        to=""
        exact
        >
            <template #prepend>
                <v-icon>mdi-calendar-today</v-icon>
            </template>
        </v-list-item>

        <v-list-item
            active-color="white"  
            title="Departments"
            to="/patient/departments"
            >
            <template #prepend>
                <v-icon>mdi-hospital-building</v-icon>
            </template>
        </v-list-item>
    </v-navigation-drawer>
</template>