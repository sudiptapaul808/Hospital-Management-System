<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import router from '../../router/index.js';
import { useRoute, useRouter } from 'vue-router'
import CreateAvailabilityModal from '../../components/doctor/CreateAvailabilityModal.vue';
import { propsFactory } from 'vuetify/lib/util/propsFactory.mjs';

const route = useRoute()
const date = route.params.date

const availabilityDetails = ref([])

//fetch details=================================================================================================
const fetchDetails = async() => {
    try {
        const res = await api.get(`/api/doctor/availability`,{
            params: {
                date: date
            }
        })
        console.log(res)
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchDetails()
})

//create availability==========================================================================================
const showCreate = ref(false)

//edit availability============================================================================================
const showEdit = ref(false)

//delete availability==========================================================================================
const showDelete = ref(false)
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                Availability for {{ date }}
            </v-col>
            <div class="d-flex ga-2">
                <v-btn
                color="primary"
                variant="tonal"
                @click="showCreate=true"
                >
                    Create Availability
                </v-btn>
            </div>
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
                    <td><v-btn @click="showEdit=true" variant="tonal">Edit</v-btn></td>
                    <td><v-btn @click="showDelete=true" color="seconday" variant="tonal">Delete</v-btn></td>
                </tr>
            </tbody>
        </v-table>
        <CreateAvailabilityModal 
            v-if="showCreate"
            v-model="showCreate"
            :date="date"
            @created="fetchDetails"
        />
    </div>
</template>