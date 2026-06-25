<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const patients = ref([])

//Pagination controls======================================================================================
const page = ref(Number(route.query?.page) || 1)
const perPage = ref(10)
const total = ref(0)

const totalPages = computed(() => {
  return Math.ceil(total.value / perPage.value)
})

const nextPage = () => {
    if (page.value < totalPages.value) {
        page.value++ 
        router.push({
            query: {
                ...route.query,
                page: page.value
            }
        })
        fetchAdmittedPatients()
    }
}
const prevPage = () => {
    if (page.value > 1) {
        page.value--
        router.push({
            query: {
                ...route.query,
                page: page.value
            }
        })
        fetchAdmittedPatients()
    }
}

//Fetch Admitted patient's list=========================================================================
const fetchAdmittedPatients = async() => {
    if (loading.value) return
    loading.value = true

    try {
        const res = await api.get(`api/admin_dashboard/admitted_patients`, {
            params: {
                patients_page: page.value,
                per_page: perPage.value
            }
        })
        console.log("FETCHING ADMITTED PATIENTS")
        patients.value = res.data.patients
        total.value = res.data.pagination.total
    } catch (err) {
        console.log(err)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchAdmittedPatients()
})

//Function to send the id to the url of the patient details page================================================
const goToPatient = (id) => {
  router.push(`/admin/admitted-patients/${id}`)
}
</script>

<template>
  <div>
    <v-row class="mb-3" align="center" justify="space-between">
      <v-col cols="auto">
        <h2>Admitted Patients</h2>
      </v-col>
    </v-row>
    <v-table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Age</th>
          <th>Gender</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="patient in patients" :key="patient.patient_id">
          <td>{{ patient.patient_name }}</td>
          <td>{{ patient.age }}</td>
          <td>{{ patient.gender }}</td>
          <td>
            <v-btn @click="goToPatient(patient.patient_id)">View</v-btn>
          </td>
        </tr>
      </tbody>
    </v-table>
    <v-row justify="center" align="center" class="mt-4">
      <v-btn
        @click="prevPage"
        :loading="loading"
        :disabled="loading || page === 1"
        color="primary"
        variant="tonal"
      >
        Prev
      </v-btn>
      <span class="mx-4">
        Page {{ page }} / {{ totalPages }}
      </span>
      <v-btn
        @click="nextPage"
        :loading="loading"
        :disabled="loading || page === totalPages"
        color="primary"
        variant="tonal"
      >
        Next
      </v-btn>
    </v-row>
  </div>
</template>