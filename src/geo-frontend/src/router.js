import {createRouter, createWebHashHistory} from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('./components/Home.vue'),
    },
    {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('./components/dashboard/Dashboard.vue'),
    },
        {
        path: '/import',
        name: 'Import',
        component: () => import('./components/import/ImportHome.vue'),
    },
    {
        path: '/import/upload',
        name: 'Import Data',
        component: () => import('./components/import/Upload.vue'),
    },
    {
        path: '/import/process/:id',
        name: 'Process Data',
        component: () => import('./components/import/Process.vue'),
        props: true
    }
]


const router = createRouter({
    history: createWebHashHistory(),
    routes
})
export default router