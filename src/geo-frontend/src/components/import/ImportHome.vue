<template>
  <div class="mb-10">
    <div>
      <a href="/#/import/upload">Upload Files</a>
    </div>

    <Importqueue/>
  </div>
</template>

<script>
import {mapState} from "vuex"
import {authMixin} from "@/assets/js/authMixin.js";
import axios from "axios";
import {IMPORT_QUEUE_LIST_URL} from "@/assets/js/import/url.js";
import {ImportQueueItem} from "@/assets/js/import/import-types.ts"
import Importqueue from "@/components/import/parts/importqueue.vue";

export default {
  computed: {
    ...mapState(["userInfo", "importQueue"]),
  },
  components: {Importqueue},
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