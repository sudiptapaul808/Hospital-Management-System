<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const appointments = ref([])

//Pagination controls====================================================================================
const page = ref(Number(route.query?.page) || 1)
const per_page = ref(10)
const total = ref(0)

const totalPages = computed(() => {
    return Math.ceil(total.value / per_page.value)
})

const nextPage = () => {
    if (page.value < totalPages.value) {
        page.value++
        router.push({
            query: {
                ...route.query,
                page: page.value
            }
        })
        fetchAppointments()
    }
}
const prevPage = () => {
    if (page.value > 1) {
        page.value--
        router.push({
            query: {
                ...route.query,
                page: page.value
            }
        })
        fetchAppointments()
    }
}

//Fetch Appointments list=======================================================================================
const fetchAppointments = async() => {
    if (loading.value) return 
    loading.value = true

    try {
        const res = await api.get(`/api/doctor/current_day_appointments`, {
            params: {
                page: page.value,
                per_page: per_page.value
            }
        })
        appointments.value = res.data.data
        total.value = res.data.pagination.total
    } catch (err) {
        console.log(err)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchAppointments()
})

//time format================================================================================================
const formatTime = (datatime) => {
    return new Date(datetime).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
    })
}

</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Appointments Scheduled today</h2>
            </v-col>
        </v-row>
        <v-table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Patient ID</th>
                    <th>Patient Name</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="appointment in appointments" :key="appointment.id">
                    <td>{{ formatTime(appointment.datetime) }}</td>
                    <td>{{ appointment.patient.id }}</td>
                    <td>{{ appointment.patient.name }}</td>
                    <td>{{ appointment.status }}</td>
                    <td>
                        <v-btn @click="">View</v-btn>
                    </td>
                </tr>
            </tbody>
        </v-table>
    </div>
</template>