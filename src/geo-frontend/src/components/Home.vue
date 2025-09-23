<template>
  <div class="prose">
    <h1>Home page</h1>
  </div>

  <div>
    <a href="/#/import">Import</a>
  </div>
</template>


<script>
import {authMixin} from "@/assets/js/authMixin.js";

export default {
  components: {},
  mixins: [authMixin],
  data() {
    return {}
  },
  methods: {},
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
};
</script>

<style scoped>
</style>
