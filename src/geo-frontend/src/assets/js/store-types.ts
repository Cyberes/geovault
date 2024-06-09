import {getCookie} from "./auth.js"

export class UserInfo {
    private username: String;
    private id: BigInteger;
    private csrftoken: String;

    constructor(username: String, userId: BigInteger) {
        this.username = username
        this.id = userId
        this.csrftoken = getCookie("csrftoken")
    }
}