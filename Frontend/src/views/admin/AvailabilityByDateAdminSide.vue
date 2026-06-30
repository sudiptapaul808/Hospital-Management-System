<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import router from '../../router/index.js';
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const doctorId = route.params.doctorId
const date = route.params.date

const doctorName = ref('')

const availabilitiesDetails = ref([])

//Fetch Details=================================================================================================
const fetchDetails = async() => {
    try {
        const res = await api.get(`/api/admin/${doctorId}/availability`, {
            params: {
                date: date
            }
        })
        console.log(res)
        availabilitiesDetails.value = res.data.availabilities_for_the_day
        doctorName.value = res.data.doctor.name
        console.log(availabilitiesDetails.value)
        console.log(doctorName.value)
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchDetails()
})
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                Availability of Dr {{ doctorName }} for {{ date }}
            </v-col>
        </v-row>
        <v-table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Department</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="availability in availabilitiesDetails" :key="availability.id">
                    <td>{{ availability.date }}</td>
                    <td>{{ availability.department_name }}</td>
                    <td>{{ availability.start_time }}</td>
                    <td>{{ availability.end_time }}</td>
                </tr>
            </tbody>
        </v-table>
    </div>
</template>