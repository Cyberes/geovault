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
    <ul class="space-y-4">
      <li v-for="(item, index) in itemsForUser" :key="`item-${index}`" class="bg-white shadow-md rounded-md p-4">
        <div class="mb-4">
          <label class="block text-gray-700 font-bold mb-2">Name:</label>
          <div class="flex items-center">
            <input v-model="item.name" :placeholder="originalItems[index].name"
                   class="border border-gray-300 rounded-md px-3 py-2 w-full"/>
            <button class="ml-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-2 px-4 rounded"
                    @click="resetField(index, 'name')">Reset
            </button>
          </div>
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 font-bold mb-2">Description:</label>
          <div class="flex items-center">
            <input v-model="item.description" :placeholder="originalItems[index].description"
                   class="border border-gray-300 rounded-md px-3 py-2 w-full"/>
            <button class="ml-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-2 px-4 rounded"
                    @click="resetField(index, 'description')">Reset
            </button>
          </div>
        </div>
        <div class="">
          <label class="block text-gray-700 font-bold mb-2">Created:</label>
          <div class="flex items-center">
            <flat-pickr :config="flatpickrConfig" :value="item.properties.created"
                        class="border border-gray-300 rounded-md px-3 py-2 w-full"
                        @on-change="updateDate(index, $event)"></flat-pickr>
            <button class="ml-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-2 px-4 rounded"
                    @click="resetNestedField(index, 'properties', 'created')">Reset
            </button>
          </div>
          <div>
            <label class="block text-gray-700 font-bold mb-2">Tags:</label>
            <div v-for="(tag, tagIndex) in item.properties.tags" :key="`tag-${tagIndex}`" class="mb-2">
              <div class="flex items-center">
                <input v-model="item.properties.tags[tagIndex]" :placeholder="getTagPlaceholder(index, tag)"
                       class="border rounded-md px-3 py-2 w-full bg-white"/>
                <button class="ml-2 bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
                        @click="removeTag(index, tagIndex)">Remove
                </button>
              </div>
            </div>
          </div>
          <div class="flex items-center mt-2">
            <button :class="{ 'opacity-50 cursor-not-allowed': isLastTagEmpty(index) }"
                    :disabled="isLastTagEmpty(index)"
                    class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
                    @click="addTag(index)">Add Tag
            </button>
            <button class="ml-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-2 px-4 rounded"
                    @click="resetTags(index)">Reset Tags
            </button>
          </div>
        </div>
      </li>
    </ul>
  </div>

  <button class="m-2 bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
          @click="saveChanges">Save
  </button>


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
import {getCookie} from "@/assets/js/auth.js";
import flatPickr from 'vue-flatpickr-component';
import 'flatpickr/dist/flatpickr.css';

// TODO: for each feature, query the DB and check if there is a duplicate. For points that's duplicate coords, for linestrings and polygons that's duplicate points
// TODO: auto-refresh if still processing

export default {
  computed: {
    ...mapState(["userInfo"]),
  },
  components: {Importqueue, flatPickr},
  data() {
    return {
      msg: "",
      currentId: null,
      itemsForUser: [],
      originalItems: [],
      workerLog: [],
      flatpickrConfig: {
        enableTime: true,
        time_24hr: true,
        dateFormat: 'Y-m-d H:i',
        timezone: 'UTC',
      },
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
    },
    resetField(index, fieldName) {
      this.itemsForUser[index][fieldName] = this.originalItems[index][fieldName];
    },
    resetNestedField(index, nestedField, fieldName) {
      this.itemsForUser[index][nestedField][fieldName] = this.originalItems[index][nestedField][fieldName];
    },
    addTag(index) {
      if (!this.isLastTagEmpty(index)) {
        this.itemsForUser[index].tags.push('');
      }
    },
    getTagPlaceholder(index, tag) {
      const originalTagIndex = this.originalItems[index].tags.indexOf(tag);
      return originalTagIndex !== -1 ? this.originalItems[index].tags[originalTagIndex] : '';
    },
    isLastTagEmpty(index) {
      const tags = this.itemsForUser[index].tags;
      return tags.length > 0 && tags[tags.length - 1].trim().length === 0;
    },
    resetTags(index) {
      this.itemsForUser[index].tags = [...this.originalItems[index].tags];
    },
    removeTag(index, tagIndex) {
      this.itemsForUser[index].tags.splice(tagIndex, 1);
    },
    updateDate(index, selectedDates) {
      this.itemsForUser[index].properties.created = selectedDates[0];
    },
    saveChanges() {
      const csrftoken = getCookie('csrftoken');
      axios.put('/api/data/item/import/update/' + this.id, this.itemsForUser, {
        headers: {
          'X-CSRFToken': csrftoken
        }
      }).then(response => {
        if (response.data.success) {
          this.msg = 'Changes saved successfully';
          window.alert(this.msg);
        } else {
          this.msg = 'Error saving changes: ' + response.data.msg;
          window.alert(this.msg);
        }
      }).catch(error => {
        this.msg = 'Error saving changes: ' + error.message;
        window.alert(this.msg);
      });
    },
  }
  ,
  beforeRouteEnter(to, from, next) {
    next(async vm => {
      if (vm.currentId !== vm.id) {
        vm.msg = ""
        vm.messages = []
        vm.itemsForUser = []
        vm.originalItems = []
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
              vm.originalItems = JSON.parse(JSON.stringify(vm.itemsForUser))
            }
            vm.msg = response.data.msg
            vm.workerLog = response.data.log
          }
        }).catch(error => {
          vm.handleError(error.message)
        })
      }
    })
  }
  ,
}

</script>

<style scoped>

</style>