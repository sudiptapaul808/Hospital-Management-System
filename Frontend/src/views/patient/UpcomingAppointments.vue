<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import CancelOpdAppointmentModal from '../../components/patient/CancelOpdAppointmentModal.vue';
import { useRouter } from 'vue-router'

const router = useRouter()

const appointments = ref([])
const referrals = ref([])

//Fetch everything=========================================================================================
const fetchData = async() => {
    try {
        const res = await api.get(`/api/patient/appointments`)
        appointments.value = res.data.appointments
        referrals.value = res.data.referrals
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchData()
})

//Cancel appointment===================================================================================================
const showCancel = ref(false)
const appointment_id = ref(null)
const openCancel = (id) => {
    appointment_id.value = id
    showCancel.value = true
}

//Send to book flow from the referral book==============================================================================
const goToDoctor = (id) => {
    router.push(`/patient/doctor-details/${id}`)
}
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Upcoming OPD Appointments</h2>
            </v-col>
        </v-row>
        <v-table v-if="appointments.length">
            <thead>
                <tr>
                    <th>Doctor Name</th>
                    <th>Department</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="appointment in appointments" :key="appointment.appointment_id">
                    <td>{{ appointment.doctor_name }}</td>
                    <td>{{ appointment.department }}</td>
                    <td>{{ appointment.date }}</td>
                    <td>{{ appointment.time }}</td>
                    <td>{{ appointment.status }}</td>
                    <td><v-btn :disabled="appointment.status !== 'booked'" @click="openCancel(appointment.appointment_id)">Cancel</v-btn></td>
                </tr>
            </tbody>
        </v-table>
        <p v-else class="text-grey">
            No scheduled appointments
        </p>


        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Pending OPD referral</h2>
            </v-col>
        </v-row>
        <div v-if="referrals">
            <v-card class="mb-4">
                <v-card-text>
                    <p><strong>From: </strong>Dr. {{ referrals.referred_by_doctor_name }}</p>
                    <p><strong>To Department: </strong>{{ referrals.referred_to_dept_name }}</p>
                    <p><strong>Doctor: </strong>Dr. {{ referrals.referred_to_doctor_name}}</p>
                </v-card-text>
                <v-card-actions>
                    <v-btn color="primary" @click="goToDoctor(referrals.referred_to_doctor_id)">
                        Book Appointment
                    </v-btn>
                </v-card-actions>
            </v-card>
        </div>
        <div v-else>
            No pending referrals
        </div>


        <CancelOpdAppointmentModal 
            v-if="showCancel"
            v-model="showCancel"
            :appointment-id="appointment_id"
            @update:modelValue="showCancel = $event"
            @cancelled="fetchData"
        />
    </div>


</template>