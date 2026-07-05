<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const departments = ref([])

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
        fetchAdmittedPatients()
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
        fetchAdmittedPatients()
    }
}

//Fetch Departments=================================================================================
const fetchDepartments = async() => {
    if (loading.value) return
    loading.value = true
    try {
        const res = await api.get(`/api/patient/department_list`, {
            params: {
                page: page.value,
                per_page: perPage.value
            }
        })
        departments.value = res.data.departments.departments
        total.value = res.data.departments.pagination.total
    } catch (err) {
        console.log(err)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchDepartments()
})

//View Department details========================================================================================
const goToDepartment = (id) => {
    router.push(`/patient/departments/${id}`)
}
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Departments</h2>
            </v-col>
        </v-row>
        <v-table>
            <thead>
                <tr>
                <th>Department Name</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="department in departments" :key="department.id">
                    <td>{{ department.department_name }}</td>
                    <td class="text-right">
                        <v-btn @click="goToDepartment(department.id)">View</v-btn>
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