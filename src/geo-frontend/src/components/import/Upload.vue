<template>
  <div class="mb-10">
    <p>import data</p>
    <p>Only KML/KMZ files supported.</p>
    <p>Be careful not to upload duplicate files of the opposite type. For example, do not upload both
      <kbd>example.kml</kbd>
      and <kbd>example.kmz</kbd>. Currently, the system can't detect duplicate cross-file types.</p>
  </div>

  <div class="relative w-[90%] m-auto">
    <div>
      <input id="uploadInput" :disabled="disableUpload" type="file" @change="onFileChange">
      <button :disabled="disableUpload" @click="upload">Upload</button>
    </div>
  </div>

  <div v-if="uploadMsg !== ''" class="w-[90%] m-auto mt-10" v-html="uploadMsg"></div>
</template>

<script>
import {mapState} from "vuex"
import {authMixin} from "@/assets/js/authMixin.js";
import axios from "axios";
import {capitalizeFirstLetter} from "@/assets/js/string.js";

// TODO: after import, don't disable the upload, instead add the new item to a table at the button and then prompt the user to continue

export default {
  computed: {
    ...mapState(["userInfo"]),
  },
  components: {},
  mixins: [authMixin],
  data() {
    return {
      file: null,
      disableUpload: false,
      uploadMsg: "",
      processQueue: []
    }
  },
  methods: {
    onFileChange(e) {
      this.file = e.target.files[0]
      const fileType = this.file.name.split('.').pop().toLowerCase()
      if (fileType !== 'kmz' && fileType !== 'kml') {
        alert('Invalid file type. Only KMZ and KML files are allowed.') // TODO: have this be a message on the page?
        e.target.value = "" // Reset the input value
      }
    },
    async upload() {
      this.uploadMsg = ""
      if (this.file == null) {
        return
      }
      let formData = new FormData()
      formData.append('file', this.file)
      try {
        this.disableUpload = true
        const response = await axios.post('/api/data/item/import/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'X-CSRFToken': this.userInfo.csrftoken
          }
        })
        this.uploadMsg = `<p>${capitalizeFirstLetter(response.data.msg).trim(".")}.</p><p><a href="/#/import/process/${response.data.id}">Continue to Import</a>`
        await this.fetchQueueList()
        this.file = null
        document.getElementById("uploadInput").value = ""
        this.disableUpload = false
      } catch (error) {
        this.handleError(error)
      }
    },
    handleError(error) {
      console.error("Upload failed:", error)
      if (error.response.data.msg != null) {
        this.uploadMsg = error.response.data.msg
      }
    },
    async fetchQueueList() {
      const response = await axios.get('/api/data/item/import/get/mine')
      this.processQueue = response.data.data
    },
  },
  async created() {
  },
  async mounted() {
  },
  beforeRouteEnter(to, from, next) {
    next(async vm => {
      vm.file = null
      vm.disableUpload = false
      vm.uploadMsg = ""
      await vm.fetchQueueList()
    })
  },
  watch: {},
}
</script>

<style scoped>
</style>