import './assets/css/main.css'

import {createApp} from 'vue'
import App from './App.vue'
import store from "@/assets/js/store.ts";
import router from "@/router.js";
import DropZone from 'dropzone-vue';
import '@/assets/css/root.css'

createApp(App)
    .use(router)
    .use(store)
    .use(DropZone)
    .mount('#app')
