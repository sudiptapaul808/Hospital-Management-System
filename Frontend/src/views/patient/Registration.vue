<script setup>
import { onMounted } from 'vue'
import { ref } from 'vue'
import api from '../../services/api'
import { useRouter } from 'vue-router'

const router = useRouter()

const loading = ref(false)
const error = ref('')
const newPatient = ref({
    username: '',
    email: '',
    password: '',
    age: '',
    gender: ''
})

//Register New patient========================================================================================
const registerPatient = async() => {
    if (loading.value) return
    loading.value = true
    error.value = ''
    try {
        await api.post(`/api/patient/patient_registration`, {
            username: newPatient.value.username,
            email: newPatient.value.email,
            password: newPatient.value.password,
            age: newPatient.value.age,
            gender: newPatient.value.gender
        })
        newPatient.value = {
            username: '',
            email: '',
            password: '',
            age: '',
            gender: ''
        }
        alert("Registration Successful! Please login.")
        router.push('/login')
    } catch (err) {
        error.value = err.response?.data?.error || "Something went wrong"
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <v-container>
        <v-row justify="center">
            <v-col cols="12" md="6" lg="5">
                <v-card>
                    <v-card-title>Patient Registration</v-card-title>
                    <v-card-text>
                        <v-text-field label="Username" v-model="newPatient.username" />
                        <v-text-field label="Email" type="email" v-model="newPatient.email"/>
                        <v-text-field label="Password" type="password" v-model="newPatient.password"/>
                        <v-text-field label="Age" v-model="newPatient.age"/>
                        <v-select 
                            label="Gender"
                            :items="['Male', 'Female', 'Other']"
                            v-model="newPatient.gender"
                        />
                        <p v-if="error" class="text-red text-center">{{ error }}</p>
                        <v-btn 
                        @click="registerPatient"
                        color="secondary"
                        variant="tonal"
                        >
                            Register
                        </v-btn>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>