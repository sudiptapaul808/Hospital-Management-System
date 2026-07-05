<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import router from '../../router';

const route = useRoute()
const id = route.params.id

const department = ref({})
const doctors = ref([])

const fetchDepartmentDetails = async() => {
    try {
        const res = await api.get(`/api/patient/department/${id}/details`)
        department.value = res.data
    } catch (err) {
        console.log(err)
    }
}

const fetchDoctors = async() => {
    try {
        const res = await api.get(`/api/patient/list_doctors/${id}`)
        doctors.value = res.data.doctors_from_the_department
    } catch (err) {
        console.log(err)
    }
}

onMounted(async () => {
    await Promise.all([
        fetchDepartmentDetails(),
        fetchDoctors()
    ])
})

const goToDoctor = (id) => {
    router.push(`/patient/doctor-details/${id}`)
}
</script>

<template>
    <div class="d-flex justify-space-between align-center">
        <h1>{{ department.department_name }} Details</h1>
    </div>
    <p>{{ department.description }}</p>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Doctors from {{ department.department_name }}</h2>
            </v-col>
        </v-row>
        <v-table>
            <thead>
                <tr>
                    <th>Name</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="doctor in doctors" :key="doctor.id">
                    <td>{{ doctor.name }}</td>
                    <td class="text-right">
                        <v-btn @click="goToDoctor(doctor.id)">View</v-btn>
                    </td>
                </tr>
            </tbody>
        </v-table>
    </div>
</template>