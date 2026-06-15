<script setup>
import { onMounted, ref } from 'vue';
import { computed } from 'vue';
import api from '../../services/api'
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()

const loading = ref(false) //to prevent span clicks on action buttons
const departments = ref([])
const dialog = ref(false)
const newDepartment = ref({
    department_name: '',
    description: ''
})
const page = ref(Number(route.query?.page) || 1)
const perPage = ref(10)
const total = ref(0)

//selected department for actions
const selectedDepartment = ref({
    id: null,
    department_name: '',
    description: ''
})

//edit controls
const editDialog = ref(false)
const openEdit = (dept) => {
    selectedDepartment.value = {...dept}
    editDialog.value = true
}

//delete controls
const deleteDialog = ref(false)
const openDelete = (dept) => {
    selectedDepartment.value = {...dept}
    deleteDialog.value = true
}

const fetchDepartments = async () => {
    try {
        const res = await api.get('/api/admin_dashboard/departments', {
            params: {
                departments_page: page.value,
                per_page: perPage.value
            }
        })
        departments.value = res.data.departments
        total.value = res.data.pagination.total
    } catch (err) {
        console.log(err)
    }
}

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
        fetchDepartments()
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
        fetchDepartments()
    }
}

onMounted(() => {
    fetchDepartments()
})

const addDepartment = async () => {
    if (loading.value) return
    loading.value = true
    try {
        await api.post('/api/add_department', {
            department_name: newDepartment.value.department_name,
            description: newDepartment.value.description
        })

        await fetchDepartments()

        newDepartment.value = {
            department_name: '',
            description: ''
        }
        dialog.value = false 
    } catch (err) {
        console.log(err.response?.data || err)
    } finally {
        loading.value = false
    }
}

const updateDepartment = async () => {
    if (loading.value) return
    loading.value = true
    try {
        await api.patch(`/api/edit_department/${selectedDepartment.value.id}`, {
            department_name: selectedDepartment.value.department_name,
            description: selectedDepartment.value.description
        })
        await fetchDepartments()
        editDialog.value = false
        selectedDepartment.value = {
            id: null,
            department_name: '',
            description: ''
        }
    } catch (err) {
        console.log(err.response?.data || err)
    } finally {
        loading.value = false
    }
}

const deleteDepartment = async () => {
    if (loading.value) return
    loading.value = true
    try {
        await api.delete(`/api/delete_department/${selectedDepartment.value.id}`)
        if (departments.value.length === 1 && page.value > 1) { //This is to prevent empty table error
            page.value--
        }
        await fetchDepartments()
        deleteDialog.value = false
        selectedDepartment.value = {
            id: null,
            department_name: '',
            description: ''
        }
    } catch (err) {
        console.log(err.response?.data || err)
    } finally {
        loading.value = false
    }
}
</script>


<template>
  <div>
    <!-- v-row is flex row --><!-- vuetify prefers v-col inside v-row -->
    <!-- <div style="display: flex; justify-content: space-between; align-items: center;">
        <h2>Departments</h2>

        <v-btn color="primary">
            Add Department
        </v-btn>
    </div> -->
    <v-row class="mb-3" align="center" justify="space-between">
        <v-col cols="auto">
            <h2>Departments</h2>
        </v-col>

        <v-col cols="auto">
            <v-btn color="secondary" @click="dialog = true" prepend-icon="mdi-plus">
                Add Department
            </v-btn>
        </v-col>
    </v-row>
    <v-table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Description</th>
          <th>Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="dept in departments" :key="dept.id">
          <td>{{ dept.department_name }}</td>
          <td>{{ dept.description }}</td>
          <td>
            <div class="d-flex ga-2">
                <v-btn size="small" 
                    color="secondary" 
                    variant="tonal" 
                    @click="openEdit(dept)" 
                    prepend-icon="mdi-pencil"
                >Edit</v-btn>
                <v-btn 
                    size="small" 
                    color="error" 
                    variant="tonal" 
                    @click="openDelete(dept)" 
                    prepend-icon="mdi-delete"
                >Delete</v-btn>
            </div>
          </td>
        </tr>
      </tbody>
    </v-table>
    <v-row justify="center" align="center" class="mt-4">
        <v-btn
            @click="prevPage"
            :disabled="page === 1"
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
            :disabled="page === totalPages"
            color="primary"
            variant="tonal"
        >
            Next
        </v-btn>
    </v-row>
  </div>

<!-- ADD department MODAL -->
<v-dialog v-model="dialog" max-width="400">
    <v-card rounded="lg">
        <v-card-title>Add Department</v-card-title>
        <v-card-text>
            <v-text-field
                label="Department Name"
                v-model="newDepartment.department_name"
            />
            <v-text-field
                label="Description"
                v-model="newDepartment.description"
            />
        </v-card-text>
        <v-card-actions>
            <v-spacer />
            <v-btn text @click="dialog = false" variant="tonal">Cancel</v-btn>
            <v-btn 
                color="secondary"
                variant="tonal" 
                :loading="loading"
                :disabled="loading"
                @click="addDepartment"
            >
                Add
            </v-btn>
        </v-card-actions>
    </v-card>
</v-dialog>

<!-- Edit department modal -->
<v-dialog v-model="editDialog" max-width="400">
    <v-card rounded="lg">
        <v-card-title>Edit Department</v-card-title>

            <v-card-text>
                <v-text-field
                    label="Department Name"
                    v-model="selectedDepartment.department_name"
                />

                <v-text-field
                    label="Description"
                    v-model="selectedDepartment.description"
                />
            </v-card-text>

        <v-card-actions>
        <v-spacer />

            <v-btn text @click="editDialog = false" variant="tonal">Cancel</v-btn>

            <v-btn 
                color="secondary"
                variant="tonal" 
                :loading="loading"
                :disabled="loading"
                @click="updateDepartment"
            >
                Save
            </v-btn>
        </v-card-actions>

    </v-card>
</v-dialog>

<!-- Delete department modal -->
<v-dialog v-model="deleteDialog" max-width="400">
    <v-card rounded="lg">
        <v-card-title>Delete Department</v-card-title>
        <v-card-text>
            Are you sure you want to delete
            <strong>{{ selectedDepartment.department_name }}</strong>?
        </v-card-text>
        <v-card-actions>
            <v-spacer />

            <v-btn text @click="deleteDialog = false" variant="tonal">Cancel</v-btn>

            <v-btn 
                color="error"
                variant="tonal" 
                :loading="loading"
                :disabled="loading"
                @click="deleteDepartment"
            >
                Delete
            </v-btn>
        </v-card-actions>
    </v-card>
</v-dialog>
</template>