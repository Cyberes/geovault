import {createStore} from 'vuex'
import {UserInfo} from './types/store-types'
import {ImportQueueItem} from "@/assets/js/types/import-types";


export default createStore({
    state: {
        userInfo: UserInfo,
        importQueue: ImportQueueItem

    }, mutations: {
        userInfo(state, payload) {
            state.userInfo = payload
        },
        importQueue(state, payload) {
            state.importQueue = payload
        }
    }, getters: {
        // alertExists: (state) => (message) => {
        //     return state.siteAlerts.includes(message);
        // },
    }
})
