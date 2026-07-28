<script setup>
import { computed, onMounted } from 'vue'
import { ref } from 'vue'
import api from '../../services/api'

const props = defineProps({
    modelValue: Boolean,
    patientId: Number
})

const emit = defineEmits(['update:modelValue'])

//History variables============================================================================================
const error = ref('')
const loading = ref(false)
const newHistory = ref({
    diagnosis: '',
    medicine: '',
    test_done: ''
})

//Proper handling the closing of the modal=====================================================================
const handleClose = (val) => { 
    if (!val) { 
        newHistory.value = {
            diagnosis: '',
            medicine: '',
            test_done: ''
        }
    }
    error.value = ''
    emit('update:modelValue', val)
}

//Add history===================================================================================================
const addHistory = async() => {
    if (loading.value) return
    loading.value = true

    error.value = ''

    try {
        await api.post(`/api/doctor/opd/${props.patientId}/history/new`, {
            diagnosis: newHistory.value.diagnosis,
            medicine: newHistory.value.medicine,
            test_done: newHistory.value.test_done
        })

        emit('update:modelValue', false)

        newHistory.value = {
            diagnosis: '',
            medicine: '',
            test_done: ''
        }
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
                <v-card-title>Add History/Prescription</v-card-title>
                <v-card-text>
                    <v-text-field 
                        label="Diagnosis Note"
                        v-model="newHistory.diagnosis"
                    />
                    <v-text-field 
                        label="Prescribe Medecine"
                        v-model="newHistory.medicine"
                    />
                    <v-text-field 
                        label="Tests done"
                        v-model="newHistory.test_done"
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
                        @click="addHistory"
                    >
                        Confirm
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>