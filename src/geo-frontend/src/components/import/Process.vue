<template>
  <div v-if="msg !== ''">
    <p class="font-bold">{{ msg }}</p>
  </div>

  <!-- TODO: loading indicator -->

  <div id="importMessages">
    <h2>Messages</h2>
    <li v-for="(item, index) in workerLog" :key="`item-${index}`">
      <p class="font-bold">{{ item }}</p>
    </li>
  </div>
  <div>
    <li v-for="(item, index) in itemsForUser" :key="`item-${index}`">
      <h2>{{ item.name }}</h2>
      <pre>
        {{ item }}
      </pre>
    </li>
  </div>

  <div class="hidden">
    <!-- Load the queue to populate it. -->
    <Importqueue/>
  </div>
</template>

<script>
import {mapState} from "vuex";
import {authMixin} from "@/assets/js/authMixin.js";
import axios from "axios";
import {capitalizeFirstLetter} from "@/assets/js/string.js";
import Importqueue from "@/components/import/parts/importqueue.vue";
import {GeoFeatureTypeStrings} from "@/assets/js/types/geofeature-strings";
import {GeoPoint, GeoLineString, GeoPolygon} from "@/assets/js/types/geofeature-types";

// TODO: for each feature, query the DB and check if there is a duplicate. For points that's duplicate coords, for linestrings and polygons that's duplicate points
// TODO: auto-refresh if still processing

export default {
  computed: {
    ...mapState(["userInfo"]),
  },
  components: {Importqueue},
  data() {
    return {
      msg: "",
      currentId: null,
      itemsForUser: [],
      workerLog: []
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
      switch (item.type) {
        case GeoFeatureTypeStrings.Point:
          return new GeoPoint(item);
        case GeoFeatureTypeStrings.LineString:
          return new GeoLineString(item);
        case GeoFeatureTypeStrings.Polygon:
          return new GeoPolygon(item);
        default:
          throw new Error(`Invalid feature type: ${item.type}`);
      }
    }
  },
  beforeRouteEnter(to, from, next) {
    next(async vm => {
      if (vm.currentId !== vm.id) {
        vm.msg = ""
        vm.messages = []
        vm.itemsForUser = []
        vm.currentId = null
        axios.get('/api/data/item/import/get/' + vm.id).then(response => {
          if (!response.data.success) {
            vm.handleError(response.data.msg)
          } else {
            vm.currentId = vm.id
            if (Object.keys(response.data).length > 0) {
              response.data.geofeatures.forEach((item) => {
                vm.itemsForUser.push(vm.parseGeoJson(item))
              })
            }
            vm.msg = response.data.msg
            vm.workerLog = response.data.log
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