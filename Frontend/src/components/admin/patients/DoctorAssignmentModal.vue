<script setup>
import api from '../../../services/api'
import { usePatientStore } from '../../../stores/patient'
import { ref, watch } from 'vue'

//Modal Controls==========================================================================================
const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits([
  'update:modelValue',
  'updated'
])

const closeModal = () => {
  selectingDepartments.value = false
  selectingDoctors.value = false
  emit('update:modelValue', false)
}

const patientStore = usePatientStore()

//Fetch all departments====================================================================================
const selectingDepartments = ref(false)

const departments = ref([])

const fetchAllDepartments = async() => {
    try {
        const res = await api.get(`/api/admin/all_departments`)
        departments.value = res.data.departments
    } catch (err) {
        console.log(err)
    }
}

const goToDepartments = async () => {
    await fetchAllDepartments()
    selectingDepartments.value = true
}

//Open doctors from the departments state=====================================================================
const selectingDoctors = ref(false)
const doctors = ref([])

const selectDepartment = async (departmentId) => {
    try {
        const res = await api.get(`/api/admin/departments/${departmentId}/doctors`)
        doctors.value = res.data
    } catch (err) {
        console.log(err)
    }
}

const goToDoctors = async (departmentId) => {
    await selectDepartment(departmentId)
    selectingDepartments.value = false
    selectingDoctors.value = true
}

//Actual Assignment=========================================================================================
const selectedDoctorId = ref()
const loading = ref(false)
const error = ref('')

const confirmAssignment = async () => {
    if(loading.value) return
    loading.value = true

    try {
        await api.patch(`/api/admin/${patientStore.patientDetails.id}/assign`, {
            doctor_id: selectedDoctorId.value
        })
        emit('updated')
        closeModal()
    } catch (err) {
        error.value = err.response?.data?.error || "Something went wrong"
    } finally {
        loading.value = false
    }
}

</script>
<template>
    <v-dialog :model-value="modelValue" @update:modelValue="closeModal" max-width="600">
        <v-card rounded="lg">
            <div v-if="!selectingDepartments && !selectingDoctors">
                <v-card-title>Patient Doctor assignment details</v-card-title>
                <p>Patient name: {{ patientStore.patientDetails.name }}</p>
                <p>Assigned Doctor name: {{ patientStore.patientDetails.assigned_doctor_name || 'Not assigned' }}</p>
                <p>Assigned Doctor departments: 
                    {{ 
                        patientStore.patientDetails.assigned_department.join(', ') || 'Not assigned'    
                    }}
                </p>
                <div class="d-flex justify-end ga-2 pa-4">
                    <v-btn text @click="closeModal" variant="tonal">Close</v-btn>
                    <v-btn
                    @click="goToDepartments"
                    color="secondary"
                    variant="tonal" 
                    >Assign</v-btn>
                </div>
            </div>
            <div v-else-if="selectingDepartments">
                <v-card-title>Select Department</v-card-title>
                <div class="d-flex flex-wrap ga-2 pa-4">
                    <v-btn v-for="department in departments" :key="department.id" @click="goToDoctors(department.id)">
                        {{ department.department_name }}
                    </v-btn>
                </div>
                <div class="d-flex justify-end pa-4">
                    <v-btn text @click="selectingDepartments = false" variant="tonal">
                        Back
                    </v-btn>
                </div>
            </div>
            <div v-else-if="selectingDoctors">
                <v-card-title>Select Doctor</v-card-title>
                <div class="d-flex flex-wrap ga-2 pa-4">
                    <v-btn v-for="doctor in doctors" :key="doctor.id" @click="selectedDoctorId = doctor.id" :color="selectedDoctorId === doctor.id ? 'primary': undefined">
                        {{ doctor.name }}
                    </v-btn>
                </div>
                <div class="d-flex justify-end ga-2 pa-4">
                    <v-btn text @click="selectingDoctors = false; selectingDepartments = true; selectedDoctorId = null" variant="tonal">
                        Back
                    </v-btn>
                    <v-btn
                        @click="confirmAssignment"
                        :loading="loading"
                        :disabled="loading"
                        color="secondary"
                        variant="tonal" 
                    >
                        confirm
                    </v-btn>
                </div>
            </div>
        </v-card>
    </v-dialog>
</template>