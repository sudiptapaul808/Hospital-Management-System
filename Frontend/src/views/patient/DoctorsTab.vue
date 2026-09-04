<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const doctors = ref([])

//Pagination controls======================================================================================================
const page = ref(Number(route.query?.page) || 1)
const perPage = ref(10)
const total = ref(0)

const totalPages = computed(() => {
  return Math.ceil(total.value / perPage.value)
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
        fetchDoctors()
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
        fetchDoctors()
    }
}

//Fetch Doctor list========================================================================================================
const fetchDoctors = async() => {
    if (loading.value) return
    loading.value = true
    try {
        const res = await api.get(`/api/patient/doctors_tab`, {
            params: {
                page: page.value,
                per_page: perPage.value
            }
        })
        console.log(res)
        doctors.value = res.data.doctors.data
        total.value = res.data.doctors.pagination.total
    } catch (err) {

    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchDoctors()
})

const goToDoctor = (id) => {
    router.push(`/patient/doctor-departments/${id}`)
}
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Doctors</h2>
            </v-col>
        </v-row>
        <v-table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Departments</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="doctor in doctors" :key="doctor.doctor_id">
                    <td>{{ doctor.doctor_name }}</td>
                    <td>{{ doctor.department_names.join(', ') }}</td>
                    <td class="text-right">
                        <v-btn @click="goToDoctor(doctor.doctor_id)">View</v-btn>
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