<script setup>
import { computed, onMounted } from 'vue'
import { ref } from 'vue'
import api from '../../services/api'

const props = defineProps({
    modelValue: Boolean,
    date: Number
})

const emit = defineEmits(['update:modelValue', 'created'])

//Availability variables=======================================================================================
const error = ref('')
const loading = ref(false)
const newAvailability = ref({
    startTime: '',
    endTime: '',
    selectedDepartment: ''
})

//Modal Closing================================================================================================
const handleClose = (val) => {
    if (!val) {
        newAvailability.value = {
            startTime: '',
            endTime: '',
            selectedDepartment: ''
        }
    }
    error.value = ''
    emit('update:modelValue', val)
}

//create availability=========================================================================================
const createAvailability = async() => {
    if (loading.value) return
    loading.value = true
    error.value = ''

    try {
        await api.post(`/api/doctor/availability/create`, {
            date: props.date,
            start_time: newAvailability.value.startTime,
            end_time: newAvailability.value.endTime,
            selected_department: newAvailability.value.selectedDepartment
        })

        emit('created')
        emit('update:modelValue', false)

        newAvailability.value = {
            startTime: '',
            endTime: '',
            selectedDepartment: ''
        }
    } catch (err) {
        error.value = err.response?.data?.error || "Something went wrong"
    } finally {
        loading.value = false
    }
}

//Fetching the departments the doctor belongs to===============================================================
const departments = ref([])

const fetchDoctorDepartments = async() => {
    try {
        const res = await api.get(`/api/doctor/departments`)
        departments.value = res.data.departments
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchDoctorDepartments()
})
</script>

<template>
    <div>
        <v-dialog :model-value="modelValue"
        @update:modelValue="handleClose" max-width="400">
            <v-card rounded="lg">
                <v-card-title>Create Availability for {{ props.date }}</v-card-title>
                <v-card-text>
                    <v-text-field 
                        label="Start Time"
                        type="time"
                        v-model="newAvailability.startTime"
                    />
                    <v-text-field 
                        label="End Time"
                        type="time"
                        v-model="newAvailability.endTime"
                    />
                    <v-autocomplete 
                        v-model="newAvailability.selectedDepartment"
                        :items="departments"
                        item-title="department_name"
                        item-value="id"
                        label="Department"
                        clearable
                    />
                    <p v-if="error" class="text-red text-center">{{ error }}</p>
                </v-card-text>
                <v-card-actions>
                    <v-btn text @click="handleClose(false)" variant="tonal">Close</v-btn>
                    <v-btn
                        color="secondary"
                        variant="tonal" 
                        :loading="loading"
                        :disabled="loading"
                        @click="createAvailability"
                    >
                        Confirm
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>