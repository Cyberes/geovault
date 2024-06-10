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
      <input :disabled="disableUpload" type="file" @change="onFileChange">
      <button :disabled="disableUpload" @click="upload">Upload</button>
    </div>
  </div>

  <div v-if="uploadMsg !== ''" class="w-[90%] m-auto mt-10" v-html="uploadMsg"></div>

  <table>
    <thead>
    <tr>
      <th>File Name</th>
      <th>Features</th>
      <th></th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="(item, index) in processQueue" :key="`item-${index}`">
      <td><a :href="`/#/import/process/${item.id}`">{{ item.original_filename }}</a></td>
      <td>{{ item.feature_count }}</td>
      <td>button to delete from queue</td>
    </tr>
    </tbody>
  </table>
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
        alert('Invalid file type. Only KMZ and KML files are allowed.')
        e.target.value = '' // Reset the input value
      }
    },
    upload() {
      this.uploadMsg = ""
      if (this.file == null) {
        return
      }
      let formData = new FormData()
      formData.append('file', this.file)
      axios.post('/api/data/item/import/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-CSRFToken': this.userInfo.csrftoken
        }
      }).then(response => {
        this.uploadMsg = `<p>${capitalizeFirstLetter(response.data.msg).trim(".")}.</p><p><a href="/#/import/process/${response.data.id}">Continue to Import</a>`
        this.disableUpload = true
      }).catch(error => {
        this.handleError(error)
      })
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
    }
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
.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 9999;
}
</style>