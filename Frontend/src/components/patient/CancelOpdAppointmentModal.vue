<script setup>
import api from '../../services/api'
import { onMounted, ref } from 'vue'

const props = defineProps({
    modelValue: Boolean,
    appointmentId: Number
})

const emit = defineEmits(['update:modelValue', 'cancelled'])

const closeModal = (val) => {
    error.value = ''
    emit('update:modelValue', val)
}

const error = ref('')
const loading = ref(false)

const cancel = async() => {
    if (loading.value) return
    loading.value = true
    error.value = ''
    try {
        await api.patch(`/api/patient/appointment/${props.appointmentId}/cancel`)
        emit('cancelled')
        emit('update:modelValue', false)
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
            <v-card-title>Cancel Scheduled Appointment?</v-card-title>
            <p v-if="error" class="text-red text-center">{{ error }}</p>
            <v-card-actions>
                <v-btn text @click="closeModal(false)" variant="tonal">Close</v-btn>
                <v-btn 
                    color="error"
                    variant="tonal" 
                    :loading="loading"
                    :disabled="loading"
                    @click="cancel"
                >
                    Cancel
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>