<script setup>
import { onMounted } from 'vue'
import { ref } from 'vue'
import api from '../../services/api'

const details = ref({})

const fetchDetails = async () => {
    try {
        const res = await api.get(`/api/patient/dashboard`)
        details.value = res.data.patient
        console.log(details.value)
    } catch (err) {
        console.log(err)
    } 
}

onMounted(() => {
    fetchDetails()
})
</script>

<template>
    <div class="d-flex justify-space-between align-center">
        <h1>Patient Details</h1>
    </div>
    <p>Name: {{ details.name }}</p>
    <p>Email: {{ details.email }}</p>
    <p>IPD/OPD: {{ details.admission_status }}</p>
    <p v-if="details.assigned_doctor">Assigned Doctor: {{ details.assigned_doctor }}</p>
</template>