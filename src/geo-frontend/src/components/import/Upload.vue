<template>
  <div class="mb-10">
    <p class="text-lg font-semibold mb-2">Import Data</p>
    <p class="text-gray-600 mb-2">Only KML/KMZ files supported.</p>
    <p class="text-gray-600">
      Be careful not to upload duplicate files of the opposite type. For example, do not upload both
      <kbd class="bg-gray-200 text-gray-800 px-2 py-1 rounded">example.kml</kbd>
      and <kbd class="bg-gray-200 text-gray-800 px-2 py-1 rounded">example.kmz</kbd>. Currently, the system can't detect
      duplicate cross-file types.
    </p>
  </div>

  <div class="relative w-[90%] mx-auto">
    <div class="flex items-center">
      <input id="uploadInput" :disabled="disableUpload" class="mr-4 px-4 py-2 border border-gray-300 rounded" type="file"
             @change="onFileChange">
      <button :disabled="disableUpload" class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
              @click="upload">
        Upload
      </button>
    </div>
  </div>

  <div v-if="uploadMsg !== ''" class="w-[90%] mx-auto mt-10" v-html="uploadMsg"></div>

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
    }
  },
  methods: {
    async fetchQueueList() {
      const response = await axios.get(IMPORT_QUEUE_LIST_URL)
      const ourImportQueue = response.data.data.map((item) => new ImportQueueItem(item))
      this.$store.commit('importQueue', ourImportQueue)
    },
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
        const response = await axios.post('/api/data/item/import/upload', formData, {
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