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
        to="/doctor"
        exact
        >
            <template #prepend>
                <v-icon>mdi-view-dashboard</v-icon>
            </template>
        </v-list-item>

        <v-list-item
        active-color="white"
        title="Today's Appointments"
        to="/doctor/appointments-today"
        exact
        >
            <template #prepend>
                <v-icon>mdi-calendar-today</v-icon>
            </template>
        </v-list-item>

        <v-list-item
        active-color="white"
        title="Assigned Patients"
        to="/doctor/assigned-patients"
        exact
        >
            <template #prepend>
                <v-icon>mdi-bed</v-icon>
            </template>
        </v-list-item>
        <v-list-item
        active-color="white"
        title="Availabilities"
        to="/doctor/availabilities"
        exact
        >
            <template #prepend>
                <v-icon>mdi-calendar-clock</v-icon>
            </template>
        </v-list-item>
    </v-navigation-drawer>
</template>