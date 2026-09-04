<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const id = route.params.id

const doctorDetails = ref({})

const fetchDetails = async () => {
    try {
        const res = await api.get(`/api/patient/doctor/${id}/details`)
        console.log(res)
        doctorDetails.value = res.data
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchDetails()
})

const goToAvailabilities = () => {
    router.push({
        path: `/patient/view-availabilities/${id}`,
        query: {
            departmentId: route.query.departmentId
        }
    })
}
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Dr {{ doctorDetails.doctor_name }} Details</h2>
            </v-col>
            <v-col cols="auto">
                <v-btn color="secondary" @click="goToAvailabilities">
                    OPD Timings
                </v-btn>
            </v-col>
        </v-row>
    </div>
    <div>
        <!-- <p>Departments: {{ doctorDetails.departments?.join(", ") }}</p> -->
        <p>Departments: {{ doctorDetails.departments?.map(dept => dept.name).join(", ") }}</p>
    </div>
</template>