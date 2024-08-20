import {getCookie} from "./auth.js"

export class UserInfo {
    username: String;
    id: BigInteger;
    csrftoken: String;

    constructor(username: String, userId: BigInteger) {
        this.username = username
        this.id = userId
        this.csrftoken = getCookie("csrftoken")
    }
}