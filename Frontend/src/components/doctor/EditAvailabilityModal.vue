<script setup>
import { computed, onMounted } from 'vue'
import { ref } from 'vue'
import api from '../../services/api'
import { id } from 'vuetify/locale'

const props = defineProps({
    modelValue: Boolean,
    availabilityId: Number
})

const availabilityId = props.availabilityId

const emit = defineEmits(['update:modelValue', 'updated'])

//Availability Variables======================================================================================
const error = ref('')
const loading = ref(false)
const availability = ref({
    id: '',
    date: '',
    startTime: '',
    endTime: '',
    selectedDepartment: ''
})

//Modal Closing================================================================================================
const handleClose = (val) => {
    if (!val) {
        availability.value = {
            id: '',
            date: '',
            startTime: '',
            endTime: '',
            selectedDepartment: ''
        }
    }
    error.value = ''
    emit('update:modelValue', val)
}

//update availability========================================================================================
const updateAvailability = async() => {
    if (loading.value) return
    loading.value = true
    error.value = ''
    try {
        await api.patch(`/api/doctor/availability/${availability.value.id}/update`, {
            start_time: availability.value.startTime,
            end_time: availability.value.endTime,
            selected_department: availability.value.selectedDepartment
        })
        emit('updated')
        emit('update:modelValue', false)

        availability.value = {
            id: '',
            date: '',
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


//Fetch availability to populate the fields before editing===================================================
const fetchAvailability = async() => {
    try {
        const res = await api.get(`/api/doctor/availability/${availabilityId}`)
        availability.value = {
            id: res.data.id,
            date: res.data.date,
            startTime: res.data.start_time,
            endTime: res.data.end_time,
            selectedDepartment: res.data.department_id
        }
        console.log(availability.value.selectedDepartment)
        console.log(typeof availability.value.selectedDepartment)
    } catch (err) {
        console.log(err)
    }
}
//Fetch department the doctor belongs to for the dropdown====================================================
const departments = ref([])

const fetchDoctorDepartments = async() => {
    try {
        const res = await api.get(`/api/doctor/departments`)
        departments.value = res.data.departments
        console.log(departments.value)
        console.log(typeof departments.value[0].id)
    } catch (err) {
        console.log(err)
    }
}
//Ready them up upon mounting the modal======================================================================
onMounted(async() => {
    await Promise.all([
        fetchAvailability(),
        fetchDoctorDepartments()
    ])
})

</script>

<template>
    <div>
        <v-dialog :model-value="modelValue"
        @update:modelValue="handleClose" max-width="400">
            <v-card rounded="lg">
                <v-card-title>Create Availability for {{ availability.date }}</v-card-title>
                <v-card-text>
                    <v-text-field 
                        label="Start Time"
                        type="time"
                        v-model="availability.startTime"
                    />
                    <v-text-field 
                        label="End Time"
                        type="time"
                        v-model="availability.endTime"
                    />
                    <v-autocomplete 
                        v-model="availability.selectedDepartment"
                        :items="departments"
                        item-title="department_name"
                        item-value="id"
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
                        @click="updateAvailability"
                    >
                        Confirm
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>