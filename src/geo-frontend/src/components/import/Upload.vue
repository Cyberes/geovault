<template>
  <div class="mb-10">
    <p>import data</p>
    <p>Only KML/KMZ files supported.</p>
  </div>

  <div class="relative w-[90%] m-auto">
    <div>
      <input :disabled="disableUpload" type="file" @change="onFileChange">
      <button :disabled="disableUpload" @click="upload">Upload</button>
    </div>
  </div>

  <div v-if="uploadMsg !== ''" class="w-[90%] m-auto mt-10" v-html="uploadMsg">
  </div>
</template>

<script>
import {mapState} from "vuex"
import {authMixin} from "@/assets/js/authMixin.js";
import axios from "axios";
import {capitalizeFirstLetter} from "@/assets/js/string.js";

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
      uploadMsg: ""
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
      let formData = new FormData();
      formData.append('file', this.file);
      axios.post('/api/item/import/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-CSRFToken': this.userInfo.csrftoken
        }
      }).then(response => {
        this.uploadMsg = `<p>${capitalizeFirstLetter(response.data.msg).trim(".")}.</p><p><a href="/#/import/process/${response.data.id}">Continue to Import</a>`
        this.disableUpload = true
      }).catch(error => {
        this.handleError(error)
      });
    },
    handleError(error) {
      console.log(error);
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