<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'

const appointments = ref([])
const referrals = ref([])

//Fetch everything=========================================================================================
const fetchData = async() => {
    try {
        const res = await api.get(`/api/patient/appointments`)
        appointments.value = res.data.appointments
        referrals.value = res.data.referrals
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchData()
})
</script>

<template>
    <h1>Here the upcoming 5 nearest appointments will be shown (if there are any)</h1>
    <h1>Also OPD referrals will be shown</h1>
</template>