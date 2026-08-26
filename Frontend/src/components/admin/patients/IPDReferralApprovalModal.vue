<script setup>
import api from '../../../services/api'
import { ref } from 'vue'
import router from '../../../router/index.js';

const props = defineProps({
    modelValue: Boolean,
    referralId: Number
})

const emit = defineEmits(['update:modelValue', 'approved'])

const error = ref('')
const loading = ref(false)

//handling closing of modal====================================================================================
const handleClose = (val) => {
    error.value = ''
    emit('update:modelValue', val)
}

//Approve IPD referral=========================================================================================
const approveIpdReferral = async() => {
    if (loading.value) return
    loading.value = true
    error.value = ''
    try {
        await api.patch(`/api/admin/ipd_referral/${props.referralId}/complete`)
        emit('approved')
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
                <v-card-title>Approve Referral?</v-card-title>
                <p v-if="error" class="text-red text-center">{{ error }}</p>
                <v-card-actions>
                    <v-btn text @click="handleClose(false)" variant="tonal">Close</v-btn>
                    <v-btn
                        color="secondary"
                        variant="tonal" 
                        :loading="loading"
                        :disabled="loading"
                        @click="approveIpdReferral"
                    >
                        Confirm
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>