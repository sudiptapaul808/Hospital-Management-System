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
    <div v-if="!isAdmittedFlow">
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Upcoming Appointments</h2>
            </v-col>
        </v-row>
        <v-table v-if="upcomingAppointments.length">
            <thead>
                <tr>
                    <th>Doctor Name</th>
                    <th>Department</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="appointment in upcomingAppointments" :key="appointment.id">
                    <td>{{ appointment.doctor_name }}</td>
                    <td>{{ appointment.department_name }}</td>
                    <td>{{ appointment.date }}</td>
                    <td>{{ appointment.start_time }}</td>
                    <td>{{ appointment.status }}</td>
                </tr>
            </tbody>
        </v-table>
        <p v-else class="text-grey">
            No scheduled appointments
        </p>
    </div>
    <div v-if="!isAdmittedFlow">
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Passed Appointments</h2>
            </v-col>
        </v-row>
        <v-table v-if="pastAppointments.length">
            <thead>
                <tr>
                    <th>Doctor Name</th>
                    <th>Department</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="appointment in pastAppointments" :key="appointment.id">
                    <td>{{ appointment.doctor_name }}</td>
                    <td>{{ appointment.department_name }}</td>
                    <td>{{ appointment.date }}</td>
                    <td>{{ appointment.start_time }}</td>
                    <td>{{ appointment.status }}</td>
                </tr>
            </tbody>
        </v-table>
        <p v-else class="text-grey">
            No appointment history for this patient
        </p>
    </div>
    <div v-if="!isAdmittedFlow">
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Pending OPD referrals</h2>
            </v-col>
        </v-row>
        <v-table v-if="pendingReferrals.length">
            <thead>
                <tr>
                    <th>Referred By</th>
                    <th>Referred To</th>
                    <th>Department</th>
                    <th>Date of referral</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="referral in pendingReferrals" :key="referral.id">
                    <td>{{ referral.referred_by_doctor_name}}</td>
                    <td>{{ referral.referred_to_doctor_name }}</td>
                    <td>{{ referral.referred_to_department_name }}</td>
                    <td>{{ referral.referral_date }}</td>
                </tr>
            </tbody>
        </v-table>
        <p v-else class="text-grey">
            No pending referrals for the patient
        </p>
    </div>
</template>