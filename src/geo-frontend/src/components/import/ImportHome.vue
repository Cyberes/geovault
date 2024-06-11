<template>
  <div class="mb-10">
    <div>
      <a href="/#/import/upload">Upload Files</a>
    </div>
    <div>
      <button @click="fetchQueueList">Refresh</button>
    </div>

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
        <td>
          <a :href="`/#/import/process/${item.id}`">{{ item.original_filename }}</a>
        </td>
        <td>
          {{ item.processing === true ? "processing" : item.feature_count }}
        </td>
        <td>
          <button @click="deleteItem(item.id)">Delete</button>
        </td>
      </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import {mapState} from "vuex"
import {authMixin} from "@/assets/js/authMixin.js";
import axios from "axios";


export default {
  computed: {
    ...mapState(["userInfo"]),
  },
  components: {},
  mixins: [authMixin],
  data() {
    return {
      processQueue: []
    }
  },
  methods: {
    async fetchQueueList() {
      const response = await axios.get('/api/data/item/import/get/mine')
      this.processQueue = response.data.data
    },
    async deleteItem(id) {
      try {
        const response = await axios.delete('/api/data/item/import/delete/' + id, {
          headers: {
            'X-CSRFToken': this.userInfo.csrftoken
          }
        })
        await this.fetchQueueList()
      } catch (error) {
        alert(`Failed to delete ${id}: ${error.message}`)
      }
    }
  },
  async created() {
    await this.fetchQueueList()
  },
  // async mounted() {
  // },
  // beforeRouteEnter(to, from, next) {
  //   next(async vm => {
  //   })
  // },
  watch: {},
}
</script>

<style scoped>
</style>