<script setup>
import { onMounted, ref } from 'vue'
import api from '../../services/api'

const error = ref('')
const loading = ref(false)

const props = defineProps({
    modelValue: Boolean,
    doctorId: Number,
    date: String,
    slot: Object
})

const appointmentDateTime = `${props.date}T${props.slot.start_time}:00`

const emit = defineEmits(['update:modelValue', 'booked'])

const closeModal = (val) => {
    error.value = ''
    emit('update:modelValue', val)
}

const book = async() => {
    if (loading.value) return
    loading.value = true
    error.value = ''
    try {
        await api.patch(`/api/patient/book`, {
            doctor_id: props.doctorId,
            appointment_datetime: appointmentDateTime
        })
        emit('booked')
        emit('update:modelValue', false)
    } catch (err) {
        error.value = err.response?.data?.error || "Something went wrong"
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    console.log("mounted")
    console.log('props=', props)
    console.log('modelValue=', props.modelValue)
    console.log(appointmentDateTime)
})

</script>

<template>
    <v-dialog :model-value="modelValue" @update:modelValue="closeModal" max-width="600">
        <v-card rounded="lg">
            <v-card-title>Book for {{ props.slot.start_time }} on {{ props.date }}</v-card-title>
            <p v-if="error" class="text-red text-center">{{ error }}</p>
            <v-card-actions>
                <v-btn text @click="closeModal(false)" variant="tonal">Close</v-btn>
                <v-btn 
                    color="secondary"
                    variant="tonal" 
                    :loading="loading"
                    :disabled="loading"
                    @click="book"
                >
                    Book
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>