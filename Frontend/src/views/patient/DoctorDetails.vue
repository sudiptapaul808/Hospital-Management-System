<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const id = route.params.id

const doctorDetails = ref({})

const fetchDetails = async () => {
    try {
        const res = await api.get(`/api/patient/doctor/${id}/details`)
        console.log(res)
        doctorDetails.value = res.data
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
        <h1>Dr {{ doctorDetails.doctor_name }} Details</h1>
    </div>
    <div>
        <p>Departments: {{ doctorDetails.departments?.join(", ") }}</p>
    </div>
</template>