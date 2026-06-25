<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';
import router from '../../router/index.js';

const route = useRoute()
const id = route.params.id

const histories = ref([])
const patientName = ref()

const loading = ref(false)

//Pagination controls======================================================================================
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
        fetchHistories()
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
        fetchHistories()
    }
}

//Fetch Patient Histories======================================================================================
const fetchHistories = async() => {
    if (loading.value) return
    loading.value = true
    try {
        const res = await api.get(`/api/doctor/${id}/history`, {
            params: {
                page: page.value,
                per_page: perPage.value
            }
        })
        histories.value = res.data.histories.data
        patientName.value = res.data.patient_name
        total.value = res.data.histories.pagination.total
    } catch (err) {
        console.log(err)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchHistories()
})
</script>

<template>
    <div v-if="histories.length > 0">
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>{{ patientName }}'s Medical History'</h2>
            </v-col>
        </v-row>
        <v-table>
            <thead>
                <tr>
                    <th>Doctor Name</th>
                    <th>Department Name</th>
                    <th>Visit Type</th>
                    <th>Tests Done</th>
                    <th>Date</th>
                    <th>Diagnosis</th>
                    <th>Medicine</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="history in histories" :key="history.id">
                    <td>{{ history.doctor_name }}</td>
                    <td>{{ history.department }}</td>
                    <td>{{ history.visit_type }}</td>
                    <td>{{ history.test_done }}</td>
                    <td>{{ history.diagnosis_date }}</td>
                    <td>{{ history.diagnosis }}</td>
                    <td>{{ history.medicine }}</td>
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
                prev
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
    <div v-else>
        No Previous Medical history available for {{ patientName }}.
    </div>
</template>