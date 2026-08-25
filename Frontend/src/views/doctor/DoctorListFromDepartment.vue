<script setup>
import api from '../../services/api'
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router'
import ReferralModalOpd from '../../components/doctor/ReferralModal.vue';


const route = useRoute()
const departmentId = route.params.departmentId
const patientId = route.params.patientId
const departmentName = ref(null)
const doctors = ref([])

const fetchDoctors = async() => {
    try {
        const res = await api.get(`/api/list_doctors/${departmentId}`)
        departmentName.value = res.data.department_name
        doctors.value = res.data.doctors
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchDoctors()
})

//Show the referral confirmation modal=====================================================================================
const referToDoctorId = ref(null)
const referToDoctorName = ref(null)
const showReferral = ref(false)

const showReferralModal = (id, name) => {
    referToDoctorId.value = id
    referToDoctorName.value = name
    showReferral.value = true
}


</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Doctor List from {{ departmentName }}</h2>
            </v-col>
        </v-row>
        <v-table>
            <thead>
                <tr>
                    <th>Name</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="doctor in doctors" :key="doctor.doctor_id">
                    <td>{{ doctor.doctor_name }}</td>
                    <td class="text-right">
                        <v-btn @click="showReferralModal(doctor.doctor_id, doctor.doctor_name)">Refer</v-btn>
                    </td>
                </tr>
            </tbody>
        </v-table>
    </div>
    <ReferralModalOpd 
        v-if="showReferral"
        v-model="showReferral"
        :patient-id="patientId"
        :referred-to-department-id="departmentId"
        :referred-to-department-name="departmentName"
        :referred-to-doctor-id="referToDoctorId"
        :referred-to-doctor-name="referToDoctorName"
    />
</template>