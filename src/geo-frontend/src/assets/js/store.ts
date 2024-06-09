import {createStore} from 'vuex'
import {UserInfo} from './store-types'

export default createStore({
    state: {
        userInfo: UserInfo
    }, mutations: {
        userInfo(state, payload) {
            state.userInfo = payload
        }
    }, getters: {
        // alertExists: (state) => (message) => {
        //     return state.siteAlerts.includes(message);
        // },
    }
})
