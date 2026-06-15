<script setup>
import { usePatientStore } from '../../../stores/patient'
import { ref, watch } from 'vue'
import api from '../../../services/api'

//Modal controls=============================================================================================
const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits([
  'update:modelValue',
  'updated'
])

const closeModal = () => {
  editError.value = ''
  editPatient.value = {
    id: '',
    username: '',
    email: '',
    age: '',
    gender: '',
    admission: ''
  }
  emit('update:modelValue', false)
}

//Populate the variable=============================================================================================
const patientStore = usePatientStore()

const editPatient = ref({
  id: '',
  username: '',
  email: '',
  age: '',
  gender: '',
  admission: ''
})

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      editPatient.value = {
        id: patientStore.patientDetails.id,
        username: patientStore.patientDetails.name,
        email: patientStore.patientDetails.email,
        age: patientStore.patientDetails.age,
        gender: patientStore.patientDetails.gender,
        admission: patientStore.patientDetails.is_admitted
      }
    }
  }
)

//Edit Patient==================================================================================================
const editError = ref('')
const loading = ref(false)

const editPatientConfirm = async() => {
  if(loading.value) return
  loading.value = true

  editError.value = ''
  
  try {
    await api.put(`/api/admin/patient/${editPatient.value.id}/edit`, {
      username: editPatient.value.username,
      email: editPatient.value.email,
      age: editPatient.value.age,
      gender: editPatient.value.gender,
      admission: editPatient.value.admission
    })
    emit('updated')
    closeModal()
  } catch (err) {
    editError.value = err.response?.data?.error || "Something went wrong"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <v-dialog :model-value="modelValue" @update:modelValue="closeModal" max-width="600">
    <v-card rounded="lg">
      <v-card-title>Edit Patient</v-card-title>
      <v-card-text>
        <v-text-field 
          label="Patient name"
          v-model="editPatient.username"
        />
        <v-text-field 
          label="Email"
          v-model="editPatient.email"
        />
        <v-text-field 
          label="Age"
          v-model="editPatient.age"
        />
        <v-select 
          label="Gender"
          :items="['Male', 'Female', 'Other']"
          v-model="editPatient.gender"
        />
        <v-switch v-if="!patientStore.patientDetails.is_admitted"
          label="Admit patient?"
          v-model="editPatient.admission"
        />
        <div v-else>
          <p>Patient Status: Admitted</p>
          <p>
            Assigned Doctor: {{ patientStore.patientDetails.assigned_doctor_name || 'Doctor not assigned yet' }}
          </p>
        </div>
        <p v-if="editError" class="text-red text-center">{{ editError }}</p>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="closeModal" variant="tonal">Close</v-btn>
        <v-btn 
          color="secondary"
          variant="tonal" 
          :loading="loading"
          :disabled="loading"
          @click="editPatientConfirm"
        >
          Confirm
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>