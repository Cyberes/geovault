<template>
  <div v-if="msg !== ''">
    <p>{{ msg }}</p>
  </div>

  <div>
    <li v-for="(item, index) in geoJsonData" :key="`item-${index}`">
      <pre>
        {{ parseGeoJson(item) }}
      </pre>
    </li>
  </div>
</template>

<script>
import {mapState} from "vuex";
import {authMixin} from "@/assets/js/authMixin.js";
import axios from "axios";
import {capitalizeFirstLetter} from "@/assets/js/string.js";

export default {
  computed: {
    ...mapState(["userInfo"]),
  },
  components: {},
  data() {
    return {
      msg: "",
      geoJsonData: {},
    }
  },
  mixins: [authMixin],
  props: ['id'],
  methods: {
    handleError(responseMsg) {
      console.log(responseMsg)
      this.msg = capitalizeFirstLetter(responseMsg).trim(".") + "."
    },
    parseGeoJson(item) {
      return item
    }
  },
  created() {
    axios.get('/api/item/import/get/' + this.id).then(response => {
      if (!response.data.success) {
        this.handleError(response.data.msg)
      } else {
        this.geoJsonData = response.data.data
      }
    }).catch(error => {
      this.handleError(error.message)
    });
  },
};
</script>

<style scoped>

</style>