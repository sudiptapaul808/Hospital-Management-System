<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';
import AddPatientModal from '../../components/admin/patients/AddPatientModal.vue';

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const patients = ref([])

//Pagination controls =======================================================================================
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
        fetchPatients()
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
        fetchPatients()
    }
}

//Fetch Patient's list =======================================================================================
const fetchPatients = async() => {
  if (loading.value) return
  loading.value = true

  try {
    const res = await api.get(`/api/admin_dashboard/patients`, {
      params: {
        patients_page: page.value,
        per_page: perPage.value
      }
    })
    patients.value = res.data.patients
    total.value = res.data.pagination.total
  } catch (err) {
    console.log(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPatients()
})

//Add patient modal controls===============================================================================
const showAdd = ref(false)

//Function to send the id to the url of patient details page===============================================
//This has been setup in the index.js routes
const goToPatient = (id) => {
  router.push(`/admin/patients/${id}`)  //This path has been defined in the frontend(index.js) vue not the backend
}
</script>

<template>
  <div>
    <v-row class="mb-3" align="center" justify="space-between">
      <v-col cols="auto">
        <h2>Patients</h2>
      </v-col>
      <v-col cols="auto">
        <v-btn color="secondary" @click="showAdd = true" prepend-icon="mdi-plus">
          Add new Patient
        </v-btn>
      </v-col>
    </v-row>
    <v-table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Age</th>
          <th>Gender</th>
          <th>IPD/OPD</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="patient in patients" :key="patient.patient_id">
          <td>{{ patient.patient_name }}</td>
          <td>{{ patient.age }}</td>
          <td>{{ patient.gender }}</td>
          <td>{{ patient.admission ? 'IPD' : 'OPD' }}</td>
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
    <AddPatientModal
      :modelValue="showAdd"
      @update:modelValue="showAdd = $event"
      @created="fetchPatients"
    />
  </div>
</template>