<script setup>
import { usePatientStore } from '../../../stores/patient'
import { ref, watch } from 'vue'
import api from '../../../services/api'

const blacklistError = ref('')
const loading = ref(false)

//Modal controls =============================================================================================
const props = defineProps({
    modelValue: Boolean  //This controls the opening and closing of the modal FROM the parent
})

const emit = defineEmits([
    'update:modelValue', //This emit is to let the child control the opening and closing of the modal from here
    'updated' //And this emit is to let the parent know something has updated and that now the parent should refresh
])

const closeModal = () => {
    blacklistError.value = ''
    patientToBlacklist.value = {
        id: '',
        username: '',
        blacklisted: false
    }
    emit('update:modelValue', false)
}

//Populate the variables========================================================================================
const patientStore = usePatientStore()

const patientToBlacklist = ref({
    id: '',
    username: '',
    blacklisted: false
})

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      patientToBlacklist.value = {
        id: patientStore.patientDetails.id,
        username: patientStore.patientDetails.name,
        blacklisted: patientStore.patientDetails.blacklisted
      }
    }
  }
)

//Toggle Blacklist===========================================================================================
const toggleBlacklist = async() => {
    if (loading.value) return
    loading.value = true

    blacklistError.value = ''
    try {
        await api.patch(`/api/admin/${patientToBlacklist.value.id}/toggle_blacklist`, {
            //No Payload
        })
        emit('updated')
        closeModal()
    } catch (err) {
        blacklistError.value = err.response?.data?.error || "Something went wrong"
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <v-dialog :model-value="modelValue" @update:modelValue="closeModal" max-width="600">
        <v-card rounded="lg">
            <v-card-title
                v-if="patientToBlacklist.blacklisted"
            >Un-Blacklist Patient: {{ patientToBlacklist.username }}?</v-card-title>
            <v-card-title
                v-else
            >Blacklist Patient: {{ patientToBlacklist.username }}?</v-card-title>
            <p v-if="blacklistError" class="text-red text-center">{{ blacklistError }}</p>
            <v-card-actions>
                <v-spacer />
                <v-btn text @click="closeModal" variant="tonal">Close</v-btn>
                <v-btn 
                    :color="patientToBlacklist.blacklisted ? 'error' : 'secondary'" 
                    variant="tonal" 
                    :loading="loading"
                    :disabled="loading"
                    @click="toggleBlacklist"
                >
                    {{ patientToBlacklist.blacklisted ? 'Unblacklist' : 'Blacklist' }}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>