<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import router from '../../router';
import { useDepartmentStore } from '../../stores/department';

const departmentStore = useDepartmentStore()

const route = useRoute()
const id = route.params.id

const departmentName = ref(null)
const departmentDescription = ref(null)
const doctors = ref([])

const fetchDoctors = async() => {
    try {
        const res = await api.get(`/api/patient/list_doctors/${id}`)
        departmentStore.id = res.data.department_id
        departmentName.value = res.data.department_name
        departmentDescription.value = res.data.department_description
        doctors.value = res.data.doctors
    } catch (err) {
        console.log(err)
    }
}

onMounted(async () => {
    fetchDoctors()
})

const goToDoctor = (id) => {
    router.push(`/patient/doctor-details/${id}`)
}
</script>

<template>
    <div class="d-flex justify-space-between align-center">
        <h1>{{ departmentName }} Details</h1>
    </div>
    <p>{{ departmentDescription }}</p>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Doctors from {{ departmentName }}</h2>
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
                    <td>{{ doctor.doctor_name }}</td>
                    <td class="text-right">
                        <v-btn @click="goToDoctor(doctor.doctor_id)">View</v-btn>
                    </td>
                </tr>
            </tbody>
        </v-table>
    </div>
</template>