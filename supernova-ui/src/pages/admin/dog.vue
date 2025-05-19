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
        />
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
import { ref, computed, watch } from 'vue'
import { useTableColumns } from '@/composables/useTableColumns'
import { api } from '@/boot/axios'
import { useQuasar } from 'quasar'

export default {
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