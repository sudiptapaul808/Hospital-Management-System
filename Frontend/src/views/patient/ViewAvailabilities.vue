<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const doctorId = route.params.doctorId
const doctorName = ref('')

const availabilities = ref([])

const fetchAvailabilities = async() => {
    try {
        const res = await api.get(`/api/patient/${doctorId}/availabilities`)
        availabilities.value = res.data.availabilities
        doctorName.value = res.data.doctor.name
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchAvailabilities()
})

const goToDetails = (date) => {
    router.push(`/patient/availability/${doctorId}/${date}`)
}
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Dr {{ doctorName }} availability Details</h2>
            </v-col>
        </v-row>
        <v-table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="day in availabilities" :key="day.date">
                    <td>{{ day.date }}</td>
                    <td>{{ day.status }}</td>
                    <td><v-btn @click="goToDetails(day.date)">View</v-btn></td>
                </tr>
            </tbody>
        </v-table>
    </div>
</template>