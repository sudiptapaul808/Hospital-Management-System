<script setup>
import api from '../../services/api'
import { ref } from 'vue'
import router from '../../router/index.js';
import { usePatientStore } from '../../stores/patient.js';

const props = defineProps({
    modelValue: Boolean,
    referredToDepartmentId: Number,
    referredToDepartmentName: String,
    referredToDoctorId: Number,
    referredToDoctorName: String
})

const patientStore = usePatientStore()
const patientId = patientStore.patientDetails.id

const emit = defineEmits(['update:modelValue'])

const error = ref('')
const loading = ref(false)

const handleClose = (val) => {
    error.value = ''
    emit('update:modelValue', val)
}

//Refer Patient-====================================================================================================
const completeReferral = async() => {
    if (loading.value) return
    loading.value = true
    error.value = ''
    try {
        if (patientStore.patientDetails.is_admitted) {
            //IPD referral call
            await api.patch(`/api/refer_IPD_patients/${patientId}`, {
            referred_to_dept_id: props.referredToDepartmentId,
            referred_to_doctor_id: props.referredToDoctorId
            })
        } else {
            //OPD referral call
            await api.patch(`/api/refer_OPD_patient/${patientId}`, {
            referred_to_dept_id: props.referredToDepartmentId,
            referred_to_doctor_id: props.referredToDoctorId
        })
        }
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
        @update:modelValue="handleClose" max-width="600">
            <v-card rounded="lg">
                <v-card-title>Refer patient to Dr.{{ props.referredToDoctorName }} of {{ props.referredToDepartmentName }} Department</v-card-title>
                <p v-if="error" class="text-red text-center">{{ error }}</p>
                <v-card-actions>
                    <v-btn text @click="handleClose(false)" variant="tonal">Close</v-btn>
                    <v-btn
                        color="secondary"
                        variant="tonal" 
                        :loading="loading"
                        :disabled="loading"
                        @click="completeReferral"
                    >
                        Confirm
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>