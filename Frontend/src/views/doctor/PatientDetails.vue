<script setup>
import { usePatientStore } from '../../stores/patient.js';

import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';

const route = useRoute()
const id = route.params.id
const patientStore = usePatientStore()

const patientDetails = ref(null)
const pendingIPDReferrals = ref([])

const isAppointmetFlow = route.path.includes('appointments-today')

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

</script>

<template>
    <div class="d-flex justify-space-between align-center">
        <h1>Patient Details</h1>
        <div class="d-flex ga-2">
            <v-btn
                color="primary"
                variant="tonal"
                @click=""
            >
                View History
            </v-btn>
            <v-btn
                color="primary"
                variant="tonal"
                @click=""
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
            @click=""
        >
            Complete Appointment
        </v-btn>
        <v-btn
            v-else
            color="error"
            variant="tonal"
            @click=""
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
    </div>
</template>