
<template>
  <q-page>
    <q-card v-if="dogs.length > 0" class="my-card" flat bordered>
      <q-card-section>
        <div class="text-h6">Dogs List</div>
      </q-card-section>
      <q-card-section>
        <q-table
          :rows="dogs"
          :columns="tableColumns"
          row-key="id"
          :loading="loading"
        >
          <!-- Custom slot for main_handler_id -->
          <template v-slot:body-cell-main_handler_id="props">
            <q-td :props="props">
              <UtilCustomDisplayCard
                :id="props.value"
                icon="person"
                api-route="/handler/user-profile"
                :param-name="'handler_id'"
                :keys-to-display="['handler_name']"
              />
            </q-td>
          </template>

          <!-- Custom slot for alternate_handler_id -->
          <template v-slot:body-cell-alternate_handler_id="props">
            <q-td :props="props">
              <UtilCustomDisplayCard
                :id="props.value"
                icon="person"
                api-route="/handler/user-profile"
                :param-name="'handler_id'"
                :keys-to-display="['handler_name']"
              />
            </q-td>
          </template>

          <!-- Custom slot for current_level_type_id -->
          <template v-slot:body-cell-current_level_type_id="props">
            <q-td :props="props">
              <UtilCustomDisplayCard
                :id="props.value"
                icon="school"
                api-route="/level-type"
                :param-name="'level_type_id'"
                :keys-to-display="['name', 'description']"
              />
            </q-td>
          </template>
        </q-table>
      </q-card-section>
    </q-card>
    <div v-else-if="loading" class="flex flex-center q-pa-lg">
      <q-spinner size="48px" color="primary" />
      <div class="q-ml-md">Loading dogs data...</div>
    </div>
    <q-card v-else class="my-card" flat bordered>
      <q-card-section>
        <div class="text-h6">No Data Available</div>
        <div class="text-subtitle2">Please try again later</div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script>
import { ref } from 'vue'
import { useTableColumns } from '@/composables/useTableColumns'
import { api } from '@/boot/axios'
import { useQuasar } from 'quasar'
import UtilCustomDisplayCard from '@/components/Util/UtilCustomDisplayCard.vue'

export default {
  components: {
    UtilCustomDisplayCard // Make sure to register the component here
  },
  setup() {
    const q = useQuasar()
    return {
      q
    }
  },

  data() {
    return {
      dogs: [],
      loading: false,
      tableColumns: [] // Start with empty array
    }
  },

  watch: {
    // Watch for dogs data change to update columns
    dogs: {
      handler(newValue) {
        if (newValue && newValue.length > 0) {
          // Create a ref to pass to the composable
          const dogsRef = ref(newValue)
          // Get columns from the composable
          const { columns } = useTableColumns(dogsRef)
          // Set tableColumns to the value of the computed ref
          this.tableColumns = columns.value
        }
      },
      immediate: true,
      deep: true
    }
  },

  mounted() {
    this.getDogs()
  },

  methods: {
    async getDogs() {
      try {
        this.loading = true
        const response = await api.get('/dog')
        if (response.status !== 200) {
          this.q.notify({
            type: 'negative',
            message: 'Error fetching dogs data',
          })
          return
        }
        this.dogs = response.data
      } catch (error) {
        console.error('Error fetching dogs:', error)
        this.q.notify({
          type: 'negative',
          message: 'Error fetching dogs data',
        })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style lang="sass" scoped>
.my-card
  width: 100%
</style>