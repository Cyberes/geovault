<template>
  <div class="mb-10">
    <div>
      <a class="text-blue-500 hover:text-blue-700" href="/#/import/upload">Upload Files</a>
    </div>

    <Importqueue/>

    <div class="prose mt-10">
      <h3>Import History</h3>
    </div>
    <table class="mt-6 w-full border-collapse">
      <thead>
      <tr class="bg-gray-100">
        <th class="px-4 py-2 text-left">File Name</th>
        <th class="px-4 py-2">Date/Time Imported</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="(item, index) in history" :key="`history-${index}`" class="border-t">
        <td class="px-4 py-2">
          <a :href="`${IMPORT_HISTORY_URL()}/${item.id}`" class="text-blue-500 hover:text-blue-700">{{
              item.original_filename
            }}</a>
        </td>
        <td class="px-4 py-2 text-center">
          {{ item.timestamp }}
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
import {IMPORT_HISTORY_URL} from "@/assets/js/import/url.js";
import Importqueue from "@/components/import/parts/importqueue.vue";

export default {
  computed: {
    ...mapState(["userInfo", "importQueue"]),
  },
  components: {Importqueue},
  mixins: [authMixin],
  data() {
    return {
      history: [],
    }
  },
  methods: {
    IMPORT_HISTORY_URL() {
      return IMPORT_HISTORY_URL
    },
    async fetchHistory() {
      const response = await axios.get(IMPORT_HISTORY_URL)
      this.history = response.data.data
    },
  },
  async created() {
    await this.fetchHistory()
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