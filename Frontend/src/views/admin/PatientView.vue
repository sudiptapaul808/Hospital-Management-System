<script setup>
import { usePatientStore } from '../../stores/patient.js';

import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';
import EditPatientModal from '../../components/admin/patients/EditPatientModal.vue';
import BlacklistPatientModal from '../../components/admin/patients/BlacklistPatientModal.vue';
import DoctorAssignmentModal from '../../components/admin/patients/DoctorAssignmentModal.vue';

const route = useRoute()
const id = route.params.id
const patientStore = usePatientStore()

const patientDetails = ref(null)
const pastAppointments = ref([])
const upcomingAppointments = ref([])
const pendingReferrals = ref([])

const isAdmittedFlow = route.path.includes('admitted-patients') //This is to differentiate which path the admin followed and accordingly we show the (assign/reassign) button

const fetchDetails = async() => {
    try {
        const res = await api.get(`/api/admin/${id}/view`)
        console.log(res)
        patientStore.patientDetails = res.data.patient_details
        pastAppointments.value = res.data.past_appointments
        upcomingAppointments.value = res.data.upcoming_appointments
        pendingReferrals.value = res.data.pending_referrals
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchDetails()
})

//Edit patient controls=====================================================================================
const showEdit = ref(false)

//Toggle Blacklist controls================================================================================
const showBlacklist = ref(false)

//Assign Doctor controls====================================================================================
const showAssign = ref(false)
</script>

<template>
    <div class="d-flex justify-space-between align-center">
        <h1>Patient Details</h1>

        <div class="d-flex ga-2">
            <v-btn
            color="primary"
            variant="tonal"
            @click="showEdit = true"
            >
            Edit
            </v-btn>

            <v-btn
            v-if="isAdmittedFlow"
            color="primary"
            variant="tonal"
            @click="showAssign = true"
            >
                Assign/Re-Assign Doctor
            </v-btn>
            <v-btn
            v-else
            color="error"
            variant="tonal"
            @click="showBlacklist = true"
            >
                Toggle Blacklist
            </v-btn>
        </div>
    </div>
    <p>Name: {{ patientStore.patientDetails?.name }}</p>
    <p>Email: {{ patientStore.patientDetails?.email }}</p>
    <p>Age: {{ patientStore.patientDetails?.age }}</p>
    <p>Gender: {{ patientStore.patientDetails?.gender }}</p>
    <p>OPD/IPD: {{ patientStore.patientDetails?.is_admitted ? 'IPD' : 'OPD' }}</p>
    <p v-if="patientStore.patientDetails?.is_admitted == true">Assigned Doctor: {{ patientStore.patientDetails?.assigned_doctor_name || 'Not Assigned'}}</p>
    <p>Blacklisted?: {{ patientStore.patientDetails?.blacklisted ? 'Yes' : 'No' }}</p>

    <EditPatientModal 
        :modelValue="showEdit"
        @update:modelValue="showEdit = $event"
        @updated="fetchDetails"
    />
    <BlacklistPatientModal 
        :modelValue="showBlacklist"
        @update:modelValue="showBlacklist = $event"
        @updated="fetchDetails"
    />
    <DoctorAssignmentModal 
        :modelValue="showAssign"
        @update:modelValue="showAssign = $event"
        @updated="fetchDetails"
    />
</template>