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
    path: '/register',
    name: 'register',
    component: () => import('../views/patient/Registration.vue')
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
      },
      {
        path: 'doctor-availability/:doctorId', //This id is doctor id, cause we fetch the main availabilities list with the doctor's id
        component: () => import('../views/admin/DoctorAvailability.vue')
      },
      {
        path: 'doctor-availability/:doctorId/:date', //This id is doctor id, and a specific date of that doctor's availability
        component: () => import('../views/admin/AvailabilityByDateAdminSide.vue')
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
      },
      {
        path: 'availabilities',
        component: () => import('../views/doctor/Availabilities.vue')
      },
      {
        path: 'availabilities/:date',
        component: () => import('../views/doctor/AvailabilityByDate.vue')
      }
    ]
  }, 
  {
    path: '/patient',
    component: () => import('../layouts/PatientLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        component: () => import('../views/patient/PatientDashboard.vue')
      },
      {
        path: 'upcoming-appointments',
        component: () => import('../views/patient/UpcomingAppointments.vue')
      },
      {
        path: 'departments',
        component: () => import('../views/patient/Departments.vue')
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