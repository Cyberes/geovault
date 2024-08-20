<template>
  <div>
    <button @click="fetchQueueList">Refresh</button>
  </div>

  <table>
    <thead>
    <tr>
      <th>ID</th>
      <th>File Name</th>
      <th>Features</th>
      <th></th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="(item, index) in importQueue" :key="`item-${index}`">
      <td>
        <a :href="`/#/import/process/${item.id}`">{{ item.id }}</a>
      </td>
      <td>
        <a :href="`/#/import/process/${item.id}`">{{ item.original_filename }}</a>
      </td>
      <td>
        {{ item.processing === true ? "processing" : item.feature_count }}
      </td>
      <td>
        <button @click="deleteItem(item, index)">Delete</button>
      </td>
    </tr>
    </tbody>
  </table>
</template>

<script>
import {mapState} from "vuex";
import {authMixin} from "@/assets/js/authMixin.js";
import axios from "axios";
import {IMPORT_QUEUE_LIST_URL} from "@/assets/js/import/url.js";
import {ImportQueueItem} from "@/assets/js/types/import-types";

export default {
  computed: {
    ...mapState(["userInfo", "importQueue"]),
  },
  components: {},
  mixins: [authMixin],
  data() {
    return {}
  },
  methods: {
    async fetchQueueList() {
      const response = await axios.get(IMPORT_QUEUE_LIST_URL)
      const ourImportQueue = response.data.data.map((item) => new ImportQueueItem(item))
      this.$store.commit('importQueue', ourImportQueue)
    },
    async deleteItem(item, index) {
      if (window.confirm(`Delete "${item.original_filename}" (#${item.id})`))
        try {
          this.importQueue.splice(index, 1)
          // TODO: add a message popup when delete is completed
          const response = await axios.delete('/api/data/item/import/delete/' + item.id, {
            headers: {
              'X-CSRFToken': this.userInfo.csrftoken
            }
          })
          if (!response.data.success) {
            throw new Error("server reported failure")
          }
          await this.fetchQueueList()
        } catch (error) {
          alert(`Failed to delete ${item.id}: ${error.message}`)
          this.importQueue.splice(index, 0, item)
        }
    }
  },
  async created() {
    await this.fetchQueueList()
  },
}
</script>

<style scoped>

</style>