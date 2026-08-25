<script setup>
import api from '../../services/api.js'
import { ref, onMounted } from 'vue'
import router from '../../router/index.js';

const admissionStatus = ref('')

const props = defineProps({
    modelValue: Boolean,
    patientId: Number,
    referredToDepartmentId: Number,
    referredToDepartmentName: String,
    referredToDoctorId: Number,
    referredToDoctorName: String
})

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
        if (admissionStatus.value) {
            //IPD referral call
            await api.patch(`/api/refer_IPD_patients/${props.patientId}`, {
            referred_to_dept_id: props.referredToDepartmentId,
            referred_to_doctor_id: props.referredToDoctorId
            })
        } else {
            //OPD referral call
            await api.patch(`/api/refer_OPD_patient/${props.patientId}`, {
            referred_to_dept_id: props.referredToDepartmentId,
            referred_to_doctor_id: props.referredToDoctorId
        })
        }
        emit('update:modelValue', false)
        if (admissionStatus.value) {
            await router.push('/doctor/assigned-patients')
        } else {
            await router.push('/doctor/appointments-today')
        }
    } catch (err) {
        error.value = err.response?.data?.error || "Something went wrong"
    } finally {
        loading.value = false
    }
}

//OnMounted we fetch the admission status of the patient so that based on that we can call either opd or ipd============
const fetchAdmissionStatus = async() => {
    try {
        const res = await api.get(`/api/${props.patientId}/admission_status`)
        admissionStatus.value = res.data.is_admitted
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchAdmissionStatus()
})
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