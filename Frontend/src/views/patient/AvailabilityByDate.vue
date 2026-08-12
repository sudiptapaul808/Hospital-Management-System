<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { useDepartmentStore } from '../../stores/department';

const deparmentStore = useDepartmentStore()

const route = useRoute()
const router = useRouter()

const doctorId = route.params.doctorId
const date = route.params.date
const doctorName = ref('')

const availabilityDetails = ref([])

const fetchDetails = async() => {
    try {
        const res = await api.get(`/api/patient/${doctorId}/${deparmentStore.id}/availabilities_by_date`,{
            params: {
                date: date
            }
        })
        console.log(res)
        availabilityDetails.value = res.data.availability_details
        doctorName.value = res.data.doctor.name
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchDetails()
})

const goToSlots = (availabilityId) => {
    router.push(`/patient/slots/${availabilityId}`)
}
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
                <tr v-for="availability in availabilityDetails" :key="availability.id">
                    <td>{{ availability.date }}</td>
                    <td>{{ availability.department_name }}</td>
                    <td>{{ availability.start_time }}</td>
                    <td>{{ availability.end_time }}</td>
                    <td><v-btn @click="goToSlots(availability.id)" color="secondary">Check slot</v-btn></td>
                </tr>
            </tbody>
        </v-table>
    </div>
</template>