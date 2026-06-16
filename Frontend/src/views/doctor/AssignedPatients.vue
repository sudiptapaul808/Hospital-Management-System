<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';
import AppointmentsToday from './AppointmentsToday.vue';

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const patients = ref([])

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

//Fetch assigned patients list===============================================================================
const fetchAssignedPatients = async() => {
    if (loading.value) return 
    loading.value = true

    try {
        const res = await api.get(`/api/doctor/assigned_patients`, {
            params: {
                page: page.value,
                per_page: per_page.value
            }
        })
        patients.value = res.data.data
        total.value = res.data.pagination.total
    } catch (err) {
        console.log(err)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchAssignedPatients()
})

//send to view patient page=====================================================================================
const goToPatient = (id) => {
    router.push(`/doctor/assigned-patients/${id}`)
}
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Assigned Patients</h2>
            </v-col>
        </v-row>
        <v-table>
            <thead>
                <tr>
                    <th>Patient Id</th>
                    <th>Name</th>
                    <th>Age</th>
                    <th>Gender</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="patient in patients" :key="patient.patient_id">
                    <td>{{ patient.patient_id }}</td>
                    <td>{{ patient.name }}</td>
                    <td>{{ patient.age }}</td>
                    <td>{{ patient.gender }}</td>
                    <td>
                        <v-btn @click="goToPatient(patient.patient_id)">View</v-btn>
                    </td>
                </tr>
            </tbody>
        </v-table>
        <v-row justify="center" align="center" class="mt-4">
            <v-btn
            @click="prevPage"
            :loading="loading"
            :disabled="loading || page === 1"
            color="primary"
            variant="tonal"
            >
                Prev
            </v-btn>
            <span class="mx-4">
                Page {{ page }} / {{ totalPages }}
            </span>
            <v-btn
            @click="nextPage"
            :loading="loading"
            :disabled="loading || page === totalPages"
            color="primary"
            variant="tonal"
            >
                Next
            </v-btn>
        </v-row>
    </div>
</template>