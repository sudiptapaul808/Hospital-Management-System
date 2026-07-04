<script setup>
import { onMounted, ref } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const departments = ref([])

//Pagination controls======================================================================================
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
        fetchAdmittedPatients()
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
        fetchAdmittedPatients()
    }
}

//Fetch Departments=================================================================================

</script>