<script setup>
import api from '../../services/api'
import { ref } from 'vue'
import router from '../../router/index.js';

const props = defineProps({
    modelValue: Boolean,
    patientId: Number,
    appointmentId: Number
})

const emit = defineEmits(['update:modelValue'])

const error = ref('')
const loading = ref(false)

//handling closing of modal====================================================================================
const handleClose = (val) => {
    error.value = ''
    emit('update:modelValue', val)
}

//Complete appointment=========================================================================================
const completAppointment = async() => {
    if (loading.value) return
    loading.value = true
    error.value = ''
    try {
        await api.patch(`/api/doctor/appointment/${props.appointmentId}/complete`, {
            patient_id: props.patientId
        })
        emit('update:modelValue', false)
        await router.push('/doctor/appointments-today')
    } catch (err) {
        error.value = err.response?.data?.error || "Something went wrong"
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
                <v-card-title>Mark as Complete?</v-card-title>
                <v-card-actions>
                    <v-btn text @click="handleClose(false)" variant="tonal">Close</v-btn>
                    <v-btn
                        color="secondary"
                        variant="tonal" 
                        :loading="loading"
                        :disabled="loading"
                        @click="completAppointment"
                    >
                        Confirm
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>