<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const doctorId = route.params.doctorId  

const availabilities = ref([])
const doctorName = ref('')

//Fetch Availabilities==========================================================================================
const fetchAvailabilities = async() => {
    try {
        const res = await api.get(`/api/admin/${doctorId}/availabilities`)
        console.log(res)
        availabilities.value = res.data.availability
        doctorName.value = res.data.doctor.name
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchAvailabilities()
})

//Go to availability details=================================================================================
const goToDetails = (date) => {
    router.push(`/admin/doctor-availability/${doctorId}/${date}`)
}
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                Availability of Dr {{ doctorName }}
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