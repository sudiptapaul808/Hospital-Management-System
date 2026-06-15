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
      to="/admin"
      exact
    >
      <template #prepend>
        <v-icon>mdi-view-dashboard</v-icon>
      </template>
    </v-list-item>

    <v-list-item
      active-color="white"
      title="Patients"
      to="/admin/patients"
    >
      <template #prepend>
        <v-icon>mdi-account-group</v-icon>
      </template>
    </v-list-item>

    <v-list-item
      active-color="white"
      title="Admitted Patients"
      to="/admin/admitted-patients"
    >
      <template #prepend>
        <v-icon>mdi-bed</v-icon>
      </template>
    </v-list-item>

    <v-list-item
      active-color="white"
      title="Doctors"
      to="/admin/doctors"
    >
      <template #prepend>
        <v-icon>mdi-doctor</v-icon>
      </template>
    </v-list-item>

    <v-list-item
      active-color="white"  
      title="Departments"
      to="/admin/departments"
    >
      <template #prepend>
        <v-icon>mdi-hospital-building</v-icon>
      </template>
    </v-list-item>

  </v-navigation-drawer>
</template>