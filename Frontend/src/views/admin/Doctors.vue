<script setup>
import { onMounted, ref } from 'vue';
import { computed } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const loadingDoctors = ref(false)
const loadingActions = ref(false)
const doctors = ref([])

//pagination controls==========================================================================================
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
        fetchDoctors()
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
        fetchDoctors()
    }
}

//Fetch Doctors List=============================================================================================
const fetchDoctors = async() => {
  if (loadingDoctors.value) return
  loadingDoctors.value = true
  try {
    const res = await api.get(`/api/admin_dashboard/doctors`, {
      params: {
              doctors_page: page.value,
              per_page: perPage.value
            }
    })
    doctors.value = res.data.doctors
    total.value = res.data.pagination.total
  } catch (err) {
    console.log(err)
  } finally {
    loadingDoctors.value = false
  }
}

onMounted(() => {
    fetchDoctors()
})

//Fetching all the departments cause of the dropdown==============================================================
const departments = ref([])
const departmentsLoaded = ref(false)

const fetchDepartments = async () => {  //for the drop down
  if (departmentsLoaded.value) return
  try {
    const res = await api.get(`/api/admin_dashboard/departments?per_page=100`)
    departments.value = res.data.departments
    departmentsLoaded.value = true
  } catch (err) {
    console.log(err)
  }
}

//Add a doctor====================================================================================================
const addError = ref('')

const dialog = ref(false)
const newDoctor = ref({
  username: '',
  email: '',
  password: '',
  department_ids: []
})

const openAddDoctor = async () => {
  addError.value = ''
  if (!departments.value.length) {
    await fetchDepartments()
  }
  dialog.value = true
}

const addDoctor = async() => {
  if (loadingActions.value) return
  loadingActions.value = true

  addError.value = ''

  try {
    await api.post('/api/add_doctor', {
      username: newDoctor.value.username,
      email: newDoctor.value.email,
      password: newDoctor.value.password,
      department_ids: newDoctor.value.department_ids
    })

    await fetchDoctors()

    newDoctor.value = {
      username: '',
      email: '',
      password: '',
      department_ids: []
    }

    dialog.value = false
  } catch (err) {
    addError.value = err.response?.data?.error || "Something went wrong"
  } finally {
    loadingActions.value = false
  }
}

//Edit a doctor=================================================================================================
const editError = ref('')

const editDialog = ref(false)
const selectedDoctor = ref({
  id: null,
  username: '',
  email: '',
  password: '',
  department_ids: []
})
const openEdit = async (doc) => {
  if (!departments.value.length) {
    await fetchDepartments()
  }

  selectedDoctor.value = {
    id: doc.doctor_id,
    username: doc.doctor_name,
    email: doc.email,
    password: '',
    department_ids: doc.department_ids
  }
  editError.value = ''
  editDialog.value = true
}
const editDoctor = async () => {
  if (loadingActions.value) return
  loadingActions.value = true
  editError.value = ''

  try {
    await api.put(`/api/edit_doctor/${selectedDoctor.value.id}`, {
      username: selectedDoctor.value.username,
      email: selectedDoctor.value.email,
      password: selectedDoctor.value.password,
      department_ids: selectedDoctor.value.department_ids
    })
    await fetchDoctors()
    editDialog.value = false
    selectedDoctor.value = {
      id: null,
      username: '',
      email: '',
      password: '',
      department_ids: []
    }
  } catch (err) {
    editError.value = err.response?.data?.error || "Something went wrong"
  } finally {
    loadingActions.value = false
  }
}

//Blacklist doctors=============================================================================================
const blacklistError = ref('')
const doctorToBlacklist = ref({
  id: null,
  username: '',
  blacklisted: ''
})
const blacklistDialog = ref(false)

const openBlacklistConfirm = (doc) => {
  blacklistError.value = ''
  blacklistDialog.value = true
  doctorToBlacklist.value = {
    id: doc.doctor_id,
    username: doc.doctor_name,
    blacklisted: doc.blacklisted
  }
}

const blacklistDoctor = async() => {
  if (loadingActions.value) return
  loadingActions.value = true
  blacklistError.value = ''

  try {
    await api.patch(`/api/admin/${doctorToBlacklist.value.id}/toggle_blacklist`, {})
    await fetchDoctors()
    blacklistDialog.value = false
    doctorToBlacklist.value = {
      id: null,
      username: '',
      blacklisted: ''
    }
  } catch (err) {
    blacklistError.value = err.response?.data?.error || "Something went wrong"
  } finally {
    loadingActions.value = false
  }
}

</script>

<template>
  <div>
    <v-row class="mb-3" align="center" justify="space-between">
      <v-col cols="auto">
        <h2>Doctors</h2>
      </v-col>
      <v-col cols="auto">
        <v-btn color="secondary" @click="openAddDoctor" prepend-icon="mdi-plus">
          Add Doctor
        </v-btn>
      </v-col>
    </v-row>
    <v-table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Departments</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doc in doctors" :key="doc.doctor_id">
          <td>{{ doc.doctor_name }}</td>
          <td>{{ doc.department_names?.length ? doc.department_names.join(', ') : '—' }}</td>
          <td>
            <div class="d-flex ga-2">
              <v-btn size="small" 
                  color="secondary" 
                  variant="tonal" 
                  @click="openEdit(doc)" 
                  prepend-icon="mdi-pencil"
              >Edit</v-btn>
              <v-btn 
                  size="small" 
                  :color="doc.blacklisted ? 'error' : 'secondary'" 
                  variant="tonal" 
                  @click="openBlacklistConfirm(doc)" 
                  :prepend-icon="doc.blacklisted ? 'mdi-check-circle' : 'mdi-cancel'"
              >{{ doc.blacklisted ? 'Unblacklist' : 'Blacklist' }}</v-btn>
            </div>
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

  <!-- Add Doctor modal ======================================================================================-->
  <v-dialog v-model="dialog" max-width="400">
    <v-card rounded="lg">
      <v-card-text>
        <v-text-field
          label="Doctor Username"
          v-model="newDoctor.username"
        />
        <v-text-field
          type="email"
          label="Email"
          v-model="newDoctor.email"
        />
        <v-text-field
          type="password"
          label="Password"
          v-model="newDoctor.password"
        />
        <v-autocomplete
          v-model="newDoctor.department_ids"
          :items="departments"
          item-title="department_name"
          item-value="id"
          label="Departments"
          multiple
          chips
          clearable
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="dialog = false" variant="tonal">Cancel</v-btn>
        <v-btn 
          color="secondary"
          variant="tonal" 
          :loading="loadingActions"
          :disabled="loadingActions"
          @click="addDoctor"
        >
          Add
        </v-btn>
      </v-card-actions>
      <v-alert
        v-if="addError"
        type="error"
        variant="tonal"
        density="compact"
        class="mb-3"
      > {{ addError }} </v-alert>
    </v-card>
  </v-dialog>

  <!-- Edit Doctor Modal =====================================================================================-->
  <v-dialog v-model="editDialog" max-width="400">
    <v-card rounded="lg">
      <v-card-title>Edit Doctor {{ selectedDoctor.username }}</v-card-title>
      <v-card-text>
        <v-text-field
          label="Doctor Username"
          v-model="selectedDoctor.username"
        />
        <v-text-field
          type="email"
          label="Email"
          v-model="selectedDoctor.email"
        />
        <v-text-field
          type="password"
          label="Password"
          v-model="selectedDoctor.password"
        />
        <v-autocomplete
          v-model="selectedDoctor.department_ids"
          :items="departments"
          item-title="department_name"
          item-value="id"
          label="Departments"
          multiple
          chips
          clearable
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="editDialog = false" variant="tonal">Cancel</v-btn>
        <v-btn 
          color="secondary"
          variant="tonal" 
          :loading="loadingActions"
          :disabled="loadingActions"
          @click="editDoctor"
        >
          Save
        </v-btn>
      </v-card-actions>
      <v-alert
        v-if="editError"
        type="error"
        density="compact"
        variant="tonal"
        class="mb-3"
      > {{ editError }} </v-alert>
    </v-card>
  </v-dialog>
  <!-- blacklist doctor modal================================================================================== -->
  <v-dialog v-model="blacklistDialog" max-width="400">
    <v-card rounded="lg">
      <v-card-title>Blacklist Dr. {{ doctorToBlacklist.username }}?</v-card-title>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="blacklistDialog = false" variant="tonal">Cancel</v-btn>
        <v-btn 
          :color="doctorToBlacklist.blacklisted ? 'error' : 'secondary'" 
          variant="tonal" 
          :loading="loadingActions"
          :disabled="loadingActions"
          @click="blacklistDoctor"
        >
          {{ doctorToBlacklist.blacklisted ? 'Unblacklist' : 'Blacklist' }}
        </v-btn>
      </v-card-actions>
      <v-alert
        v-if="blacklistError"
        type="error"
        density="compact"
        variant="tonal"
        class="mb-3"
      > {{ blacklistError }} </v-alert>
    </v-card>
  </v-dialog>
</template>