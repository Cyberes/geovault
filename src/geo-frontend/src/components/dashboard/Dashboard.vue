<template>
  <a href="/#/import">Import</a>

  <p>username: {{ userInfo.username }}</p>
  <p>id: {{ userInfo.id }}</p>
</template>

<script>
import {mapState} from "vuex";
import {authMixin} from "@/assets/js/authMixin.js";

export default {
  computed: {
    ...mapState(["userInfo"]),
  },
  components: {},
  mixins: [authMixin],
  data() {
    return {}
  },
  methods: {},
  async created() {
  },
  async mounted() {
  },
  watch: {},
}
</script>

<style scoped>

</style>