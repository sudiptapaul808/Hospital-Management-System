import { defineStore } from 'pinia'

export const usePatientStore = defineStore('patient', {
    state: () =>({
        patientDetails: null
    })
})