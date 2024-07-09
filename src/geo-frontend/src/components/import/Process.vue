<template>
  <div v-if="msg !== ''">
    <p class="font-bold">{{ msg }}</p>
  </div>

  <!-- TODO: loading indicator -->

  <div id="importMessages">
    <h2>Messages</h2>
    <li v-for="(item, index) in importResponse.log" :key="`item-${index}`">
      <p class="font-bold">{{ item }}</p>
    </li>
  </div>
  <div>
    <li v-for="(item, index) in importResponse.geofeatures" :key="`item-${index}`">
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

// TODO: for each feature, query the DB and check if there is a duplicate. For points that's duplicate coords, for linestrings and polygons that's duplicate points
// TODO: auto-refresh if still processing

export default {
  computed: {
    ...mapState(["userInfo"]),
  },
  components: {},
  data() {
    return {
      msg: "",
      importResponse: {},
      currentId: null,
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
  beforeRouteEnter(to, from, next) {
    next(async vm => {
      if (vm.currentId !== vm.id) {
        vm.msg = ""
        vm.importResponse = []
        vm.currentId = null
        axios.get('/api/data/item/import/get/' + vm.id).then(response => {
          if (!response.data.success) {
            vm.handleError(response.data.msg)
          } else {
            vm.currentId = vm.id
            if (Object.keys(response.data).length > 0) {
              vm.importResponse = response.data
            }
            vm.msg = response.data.msg
          }
        }).catch(error => {
          vm.handleError(error.message)
        })
      }
    })
  },
};
</script>

<style scoped>

</style>