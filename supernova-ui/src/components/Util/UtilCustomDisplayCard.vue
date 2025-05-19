<template>
  <q-card>
    <q-card-section class="flex justify-center q-pb-xs">
      <q-icon :name="icon" size="32px"  />
    </q-card-section>
    <div v-if="data">
    <q-card-section v-for="(key, index) in keysToDisplay" :key="index" class="flex justify-center q-py-xs">
      <q-item-label v-if="data" class="text-subtitle2">
        {{ data[key] }}
      </q-item-label>
    </q-card-section>
    </div>
      <q-item-label v-else-if="error" class="text-negative">
        {{ error }}
      </q-item-label>
      <q-spinner v-else size="16px" color="primary" />
  </q-card>
</template>
<script>
import {api} from 'boot/axios'
import { useQuasar } from 'quasar'
export default {
  name: 'UtilCustomDisplayCard',
  props: {
    icon: {
      type: String,
      required: true
    },
    apiRoute: {
      type: String,
      required: true
    },
    id: {
      type: [String, Number],
      required: true
    },
    paramName: {
      type: String,
      required: true
    },
    keysToDisplay: {
      type: Array,
      required: true
    },
  },
  setup () {
    const q = useQuasar()
    return {q}
  },
  data() {
    return {
      data: null,
      loading: true,
      error: null,
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    async fetchData() {
      try {
        this.loading = true
        const response = await api.get(`${this.apiRoute}?${this.paramName}=${this.id}&single=true`)
        this.data = response.data
      } catch  {
        this.q.notify({
          type: 'negative',
          message: 'Error fetching data'
        })
        this.loading = false
        this.error = 'Error fetching data'
      } finally {
        this.loading = false
      }
    },
  },


}
</script>