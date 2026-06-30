<script setup>
import api from '../../services/api'
import { ref } from 'vue'

const props = defineProps({
    modelValue: Boolean,
    availabilityId: Number
})

const emit = defineEmits(['update:modelValue', 'deleted'])

const error = ref('')
const loading = ref(false)

//handling closing of modal====================================================================================
const handleClose = (val) => {
    error.value = ''
    emit('update:modelValue', val)
}

//Delete availability==========================================================================================
const deleteAvailability = async() => {
    if (loading.value) return
    loading.value = true
    error.value = ''
    try {
        await api.delete(`/api/doctor/availability/${props.availabilityId}/delete`)
        emit('deleted')
        emit('update:modelValue', false)
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
                <v-card-title>Delete Availability?</v-card-title>
                <v-card-actions>
                    <v-btn text @click="handleClose(false)" variant="tonal">Close</v-btn>
                    <v-btn
                        color="secondary"
                        variant="tonal" 
                        :loading="loading"
                        :disabled="loading"
                        @click="deleteAvailability"
                    >
                        Confirm
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>