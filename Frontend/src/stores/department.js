import { defineStore } from 'pinia'

export const useDepartmentStore = defineStore('department', {
    state: () =>({
        id: null
    }),
    persist: true
})