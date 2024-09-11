<template>
  <div class="mt-4">
    <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600" @click="fetchQueueList">Refresh</button>
  </div>

  <table class="mt-6 w-full border-collapse">
    <thead>
    <tr class="bg-gray-100">
      <th class="px-4 py-2 text-left">File Name</th>
      <th class="px-4 py-2 text-left">Features</th>
      <th class="px-4 py-2"></th>
    </tr>
    </thead>
    <tbody>
    <tr v-for="(item, index) in importQueue" :key="`item-${index}`" class="border-t">
      <td class="px-4 py-2">
        <a :href="`/#/import/process/${item.id}`" class="text-blue-500 hover:text-blue-700">{{
            item.original_filename
          }}</a>
      </td>
      <td class="px-4 py-2">
        {{ item.processing === true ? "processing" : item.feature_count }}
      </td>
      <td class="px-4 py-2">
        <button class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600" @click="deleteItem(item, index)">
          Delete
        </button>
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