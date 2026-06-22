import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/admin',
    component: () => import('../layouts/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        component: () => import('../views/admin/AdminSummary.vue')
      },
      {
        path: 'patients',
        component: () => import('../views/admin/Patients.vue')
      },
      {
        path: 'patients/:id',
        component: () => import('../views/admin/PatientView.vue')
      },
      {
        path: 'admitted-patients/:id',
        component: () => import('../views/admin/PatientView.vue')
      },
      {
        path: 'doctors',
        component: () => import('../views/admin/Doctors.vue')
      },
      {
        path: 'departments',
        component: () => import('../views/admin/Departments.vue')
      },
      {
        path: 'admitted-patients',
        component: () => import('../views/admin/AdmittedPatients.vue')
      }
    ]
  },
  {
    path: '/doctor',
    component: () => import('../layouts/DoctorLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        component: () => import('../views/doctor/DoctorDashboard.vue')
      },
      {
        path: 'appointments-today',
        component: () => import('../views/doctor/AppointmentsToday.vue')
      },
      {
        path: 'assigned-patients',
        component: () => import('../views/doctor/AssignedPatients.vue')
      },
      {
        path: 'assigned-patients/:id',
        component: () => import('../views/doctor/PatientDetails.vue')
      },
      {
        path: 'appointments-today/:id',
        component: () => import('../views/doctor/PatientDetails.vue')
      },
      {
        path: 'patient/:id/history',
        component: () => import('../views/doctor/ViewHistory.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

import { useUserStore } from '../stores/user'
import { components } from 'vuetify/dist/vuetify.js'

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')
  } else {
    next()
  }
})

export default router