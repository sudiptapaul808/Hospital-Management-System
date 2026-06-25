<script setup>
import { usePatientStore } from '../../stores/patient.js';

import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';
import router from '../../router/index.js';
import AddHistoryModal from '../../components/doctor/AddHistoryModal.vue';
import DischargeModal from '../../components/doctor/DischargeModal.vue';
import CompleteAppointmentModal from '../../components/doctor/CompleteAppointmentModal.vue';

const route = useRoute()
const id = route.params.id
const patientStore = usePatientStore()

const patientDetails = ref(null)
const pendingIPDReferrals = ref([])

const isAppointmetFlow = route.path.includes('appointments-today')

const appointmentId = isAppointmetFlow ? route.query.appointment : null

const fetchDetails = async() => {
    try {
        const res = await api.get(`/api/doctor/${id}/details`)
        patientStore.patientDetails = res.data.patient_details
        pendingIPDReferrals.value = res.data.pending_ipd_referral
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchDetails()
})

//View Patient History=========================================================================================
const goToHistory = (id) => {
    router.push(`/doctor/patient/${id}/history`)
}

//Add patient History Modal Controls==================================================================================
const showAddHistory = ref(false)

//Discharge Modal controls===============================================================================
const showDischarge = ref(false)

//Complete Appointment Modal controls=======================================================================
const showComplete = ref(false)

</script>

<template>
    <div class="d-flex justify-space-between align-center">
        <h1>Patient Details</h1>
        <div class="d-flex ga-2">
            <v-btn
                color="primary"
                variant="tonal"
                @click="goToHistory(patientStore.patientDetails.id)"
            >
                View History
            </v-btn>
            <v-btn
                color="primary"
                variant="tonal"
                @click="showAddHistory=true"
            >
                Add History
            </v-btn>
        </div>
    </div>
    <p>Patient ID: {{ patientStore.patientDetails?.id }}</p>
    <p>Name: {{ patientStore.patientDetails?.name }}</p>
    <p>Age: {{ patientStore.patientDetails?.age }}</p>
    <p>Gender: {{ patientStore.patientDetails?.gender }}</p>
    <div class="d-flex justify-end ga-2 mt-4">
        <v-btn
            v-if="isAppointmetFlow"
            color="primary"
            variant="tonal"
            @click="showComplete=true"
        >
            Complete Appointment
        </v-btn>
        <v-btn
            v-else
            color="error"
            variant="tonal"
            @click="showDischarge=true"
        >
            Discharge patient
        </v-btn>
        <v-btn
            color="primary"
            variant="tonal"
            @click=""
        >
            Refer Patient
        </v-btn>
        <AddHistoryModal 
            v-if="showAddHistory"
            v-model="showAddHistory"
            :patient-id="id"
        />
        <DischargeModal 
            v-if="showDischarge"
            v-model="showDischarge"
            :patient-id="id"
        />
        <CompleteAppointmentModal 
            v-if="showComplete"
            v-model="showComplete"
            :patient-id="id"
            :appointment-id="appointmentId"
        />
    </div>
</template>