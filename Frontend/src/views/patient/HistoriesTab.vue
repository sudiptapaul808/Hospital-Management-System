<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
import { computed } from 'vue';

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const histories = ref([])

//Pagination controls======================================================================================================
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
        fetchDoctors()
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
        fetchDoctors()
    }
}

//Fetch Histories paginated =================================================================================================
const fetchHistories = async() => {
    if (loading.value) return
    loading.value = true
    try {
        const res = await api.get('/api/patient/patient_history', {
            params: {
                page: page.value,
                per_page: perPage.value
            }
        })
        console.log(res)
        histories.value = res.data.histories
        total.value = res.data.histories.pagination
    } catch (err) {
        console.log(err)
    } finally {
        loading.value = false
    }
}
</script>