<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const doctorId = route.params.id

const doctorDetails = ref({})

const fetchDetails = async () => {
    try {
        const res = await api.get(`/api/patient/doctor/${doctorId}/details`)
        doctorDetails.value = res.data
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchDetails()
})

const goToAvailabilities = (deptId) => {
    router.push({
        path: `/patient/view-availabilities/${doctorDetails.value.doctor_id}`,
        query: {
            departmentId: deptId
        }
    })
}
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Doctor Details</h2>
            </v-col>
        </v-row>
        <div>
            <v-card class="mb-4">
                <v-card-text>
                    <p><strong>Name: </strong>{{ doctorDetails.doctor_name }}</p>
                    <p><strong>Departments: </strong>{{ doctorDetails.departments?.map(dept => dept.name).join(", ") }}</p>
                </v-card-text>
            </v-card>
        </div>

        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Select department</h2>
            </v-col>
        </v-row>
        <v-table>
            <thead>
                <tr>
                    <th>Department Name</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="department in doctorDetails.departments" :key="doctorDetails.departments.id">
                    <td>{{ department.name }}</td>
                    <td><v-btn @click="goToAvailabilities(department.id)">Select Department</v-btn></td>
                </tr>
            </tbody>
        </v-table>
    </div>
</template>