import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import StudentsView from '../views/StudentsView.vue'
import TeachersView from '../views/TeachersView.vue'
import CoursesView from '../views/CoursesView.vue'
import DailyScheduleView from '../views/DailyScheduleView.vue'
import StudentScheduleView from '../views/StudentScheduleView.vue'
import TeacherMonthlyView from '../views/TeacherMonthlyView.vue'

const routes = [
  { path: '/', name: 'dashboard', component: DashboardView },
  { path: '/students', name: 'students', component: StudentsView },
  { path: '/teachers', name: 'teachers', component: TeachersView },
  { path: '/courses', name: 'courses', component: CoursesView },
  { path: '/daily-schedule', name: 'daily-schedule', component: DailyScheduleView },
  { path: '/student-schedule', name: 'student-schedule', component: StudentScheduleView },
  { path: '/teacher-monthly', name: 'teacher-monthly', component: TeacherMonthlyView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
