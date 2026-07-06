<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import BookModal from '../../components/patient/BookModal.vue';

const route = useRoute()
const router = useRouter()

const availabilityId = route.params.availabilityId

const slotDetails = ref({})
const slots = ref([])

const fetchSlots = async() => {
    try {
        const res = await api.get(`/api/patient/availability/${availabilityId}/slots`)
        slotDetails.value = res.data.slot_details
        slots.value = res.data.slots
    } catch (err) {
        console.log(err)
    }
}

onMounted(() => {
    fetchSlots()
})

//Modal Controls===============================================================================================
const selectedSlot = ref(null)
const book = ref(false)
const bookModalOpen = (slot) => {
    selectedSlot.value = slot
    book.value = true
}
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                Availability of Dr {{ slotDetails.doctor_name }}
            </v-col>
        </v-row>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                For department {{ slotDetails.department_name }}
            </v-col>
        </v-row>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                Date: {{ slotDetails.date }}
            </v-col>
        </v-row>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                Start Time: {{ slotDetails.start_time }} | End Time: {{ slotDetails.end_time }}
            </v-col>
        </v-row>
        <v-row>
            <v-col
                v-for="slot in slots" :key="slot.start_time"
                cols="12"
                sm="6"
                md="4"
            >
                <v-btn
                    block
                    color="secondary"
                    :disabled="slot.status === 'booked'"
                    @click="bookModalOpen(slot)"
                >
                    {{ slot.start_time }} - {{ slot.end_time }}
                </v-btn>
            </v-col>
        </v-row>
        <BookModal 
            v-if="book"
            :doctor-id="slotDetails.doctor_id"
            :slot="selectedSlot"
            :date="slotDetails.date"
            @update:modelValue="book = $event"
            @booked="fetchSlots"
        />
    </div>
</template>