<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';
import IPDReferralCancelModal from '../../components/admin/patients/IPDReferralCancelModal.vue';

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const referrals = ref([])

//Pagination controls====================================================================================================
const page = ref(Number(route.query?.page) || 1)
const perPage = ref(10)
const total = ref(0)

const totalPages = computed(() => {
    return Math.ceil(total.value / perPage.value)
})

const nextPage = () => {
    if (page.value < totalPages.value) {
        page.value++ 
        router.push({
            query: {
                ...route.query,
                page: page.value
            }
        })
        fetchReferrals()
    }
}
const prevPage = () => {
    if (page.value > 1) {
        page.value--
        router.push({
            query: {
                ...route.query,
                page: page.value
            }
        })
        fetchReferrals()
    }
}

//Fetch Referrals===========================================================================================================
const fetchReferrals = async() => {
    if (loading.value) return
    loading.value = true

    try {
        const res = await api.get(`/api/admin_dashboard/pending_ipd_referrals`, {
            params: {
                page: page.value, 
                per_page: perPage.value
            }
        })
        referrals.value = res.data.referrals
        total.value = res.data.pagination.total
    } catch (err) {
        console.log(err)
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    fetchReferrals()
})

const selectedReferralId = ref('')

//Confirmation modal controls =========================================================================================
const showConfirm = ref(false)

//Cancellation modal controls =========================================================================================
const showCancel = ref(false)
const openCancel = (referralId) => {
    selectedReferralId.value = referralId
    showCancel.value = true
}
</script>

<template>
    <div>
        <v-row class="mb-3" align="center" justify="space-between">
            <v-col cols="auto">
                <h2>Pendindg IPD referrals</h2>
            </v-col>
        </v-row>
        <v-table>
            <thead>
                <tr>
                    <th>Patient Name</th>
                    <th>Assigned Doctor Name</th>
                    <th>Referred to Dept</th>
                    <th>Referred to Doctor</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="referral in referrals" :key="referral.referral_id">
                    <td>{{ referral.patient_name }}</td>
                    <td>{{ referral.assigned_doctor_name }}</td>
                    <td>{{ referral.referred_to_department_name }}</td>
                    <td>{{ referral.referred_to_doctor_name }}</td>
                    <td>
                        <v-btn @click="showConfirm = true">
                            Confirm
                        </v-btn>
                        <v-btn @click="openCancel(referral.referral_id)">
                            Cancel
                        </v-btn>
                    </td>
                </tr>
            </tbody>
        </v-table>
        <v-row justify="center" align="center" class="mt-4">
        <v-btn
            @click="prevPage"
            :loading="loading"
            :disabled="loading || page === 1"
            color="primary"
            variant="tonal"
        >
            Prev
        </v-btn>
        <span class="mx-4">
            Page {{ page }} / {{ totalPages }}
        </span>
        <v-btn
            @click="nextPage"
            :loading="loading"
            :disabled="loading || page === totalPages"
            color="primary"
            variant="tonal"
        >
            Next
        </v-btn>
        </v-row>
    </div>
    <div class="d-flex justify-end ga-2 mt-4">
        <IPDReferralCancelModal 
            v-if="showCancel"
            v-model="showCancel"
            :referral-id="selectedReferralId"
            @cancelled="fetchReferrals"
        />
    </div>
</template>