<template>
  <div class="prose mb-10">
    <h1 class="mb-1">Upload Data</h1>
  </div>

  <div class="mb-10">
    <p class="mb-2">Only KML/KMZ files supported.</p>
    <p class="">
      Be careful not to upload duplicate files of the opposite type. For example, do not upload both
      <kbd class="bg-gray-200 text-gray-800 px-2 py-1 rounded">example.kml</kbd>
      and <kbd class="bg-gray-200 text-gray-800 px-2 py-1 rounded">example.kmz</kbd>. Currently, the system can't detect
      duplicate cross-file types.
    </p>
  </div>

  <div class="relative w-[90%] mx-auto">
    <div class="flex items-center">
      <input id="uploadInput" :disabled="disableUpload" class="mr-4 px-4 py-2 border border-gray-300 rounded"
             type="file"
             @change="onFileChange">
      <button :disabled="disableUpload"
              class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
              @click="upload">
        Upload
      </button>
    </div>
    <div :class="{invisible: uploadProgress <= 0}" class="mt-4">
      <div class="w-full bg-gray-200 rounded-full h-2.5">
        <div :style="{ width: uploadProgress + '%' }" class="bg-blue-600 h-2.5 rounded-full"></div>
      </div>
      <div class="text-center mt-2">{{ uploadProgress }}%</div>
    </div>

    <div class="prose" v-html="uploadResponse"></div>

    <div v-if="uploadMsg !== ''" class="mt-10 max-h-40 overflow-y-auto bg-gray-200 rounded-s p-5">
      <strong>Message from Server:</strong><br>
      {{ uploadMsg }}
    </div>
  </div>

  <div class="prose mt-10">
    <h3 class="inline">Ready to Import</h3>
    <span v-if="loadingQueueList" class="italic mr-3">
    Loading...
  </span>
  </div>
  <Importqueue/>
</template>

<script>
import {mapState} from "vuex"
import {authMixin} from "@/assets/js/authMixin.js";
import axios from "axios";
import {capitalizeFirstLetter} from "@/assets/js/string.js";
import {IMPORT_QUEUE_LIST_URL} from "@/assets/js/import/url.js";
import {ImportQueueItem} from "@/assets/js/types/import-types"
import Importqueue from "@/components/import/parts/importqueue.vue";

// TODO: after import, don't disable the upload, instead add the new item to a table at the button and then prompt the user to continue

export default {
  computed: {
    ...mapState(["userInfo", "importQueue"]),
  },
  components: {Importqueue},
  mixins: [authMixin],
  data() {
    return {
      file: null,
      disableUpload: false,
      uploadMsg: "",
      uploadProgress: 0,
      loadingQueueList: false,
      uploadResponse: ""
    }
  },
  methods: {
    async fetchQueueList() {
      this.loadingQueueList = true
      const response = await axios.get(IMPORT_QUEUE_LIST_URL)
      const ourImportQueue = response.data.data.map((item) => new ImportQueueItem(item))
      this.$store.commit('importQueue', ourImportQueue)
      this.loadingQueueList = false
    },
    onFileChange(e) {
      this.file = e.target.files[0]
      const fileType = this.file.name.split('.').pop().toLowerCase()
      if (fileType !== 'kmz' && fileType !== 'kml') {
        alert('Invalid file type. Only KMZ and KML files are allowed.')
        e.target.value = "" // Reset the input value
      }
    },
    async upload() {
      this.uploadProgress = 0
      this.uploadMsg = ""
      if (this.file == null) {
        return
      }
      let formData = new FormData()
      formData.append('file', this.file)
      try {
        this.disableUpload = true
        const response = await axios.post('/api/data/item/import/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'X-CSRFToken': this.userInfo.csrftoken
          },
          onUploadProgress: (progressEvent) => { // Add this block
            this.uploadProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          },
        })
        this.uploadMsg = capitalizeFirstLetter(response.data.msg).trim(".") + "."
        this.uploadResponse = `<a href="/#/import/process/${response.data.id}">Continue to Import</a>`
        await this.fetchQueueList()
        this.file = null
        document.getElementById("uploadInput").value = ""
      } catch (error) {
        this.handleError(error)
      }
      this.disableUpload = false
    },
    handleError(error) {
      console.error("Upload failed:", error)
      if (error.response.data.msg != null) {
        this.uploadMsg = error.response.data.msg
      }
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
    })
  },
  watch: {},
}
</script>

<style scoped>
</style>