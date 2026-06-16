<script setup>
import { usePatientStore } from '../../stores/patient.js';

import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';

const route = useRoute()
const id = route.params.id
const patientStore = usePatientStore()

const patientDetails = ref(null)
const pendingIPDReferrals = ref([])

const fetchDetails = async() => {
    try {
        
    } catch (err) {
        console.log(err)
    }
}
</script>