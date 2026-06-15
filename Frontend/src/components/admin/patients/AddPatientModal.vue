<script setup>
import { computed } from 'vue'
import { ref } from 'vue'
import api from '../../../services/api'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'created'])

const handleClose = (val) => {  //val comes here to be true or false. 
  if (!val) {  //if false !false == true. So, if the modal is closing in anyway the name is gonna be set to ''
    newPatient.value = {
      username: '',
      email: '',
      password: '',
      age: '',
      gender: '',
      admission: false
    }
  }
  addError.value = ''
  emit('update:modelValue', val)
}

//Add Patient==================================================================================
const addError = ref('')
const loading = ref(false)
const newPatient = ref({
  username: '',
  email: '',
  password: '',
  age: '',
  gender: '',
  admission: false
})

const addPatient = async() => {
  if(loading.value) return
  loading.value = true

  addError.value = ''

  try {
    await api.post('/api/add_patient', {
      username: newPatient.value.username,
      email: newPatient.value.email,
      password: newPatient.value.password,
      age: newPatient.value.age,
      gender: newPatient.value.gender,
      admission: newPatient.value.admission
    })

    emit('created')
    emit('update:modelValue', false)

    newPatient.value = {
      username: '',
      email: '',
      password: '',
      age: '',
      gender: '',
      admission: false
    }
  } catch (err) {
    addError.value = err.response?.data?.error || "Something went wrong"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
  <v-dialog :model-value="modelValue"
  @update:modelValue="handleClose" max-width="400">
    <v-card rounded="lg">
      <v-card-title>Add new Patient</v-card-title>
      <v-card-text>
        <v-text-field 
          label="Patient name"
          v-model="newPatient.username"
        />
        <v-text-field 
          label="Email"
          v-model="newPatient.email"
        />
        <v-text-field 
          label="Password"
          v-model="newPatient.password"
        />
        <v-text-field 
          label="Age"
          v-model="newPatient.age"
        />
        <v-select 
          label="Gender"
          :items="['Male', 'Female', 'Other']"
          v-model="newPatient.gender"
        />
        <v-switch 
          label="Admitted?"
          v-model="newPatient.admission"
        />
        <p v-if="addError" class="text-red text-center">{{ addError }}</p>
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="handleClose(false)" variant="tonal">Close</v-btn>
        <v-btn 
          color="secondary"
          variant="tonal" 
          :loading="loading"
          :disabled="loading"
          @click="addPatient"
        >
          Confirm
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  </div>
</template>