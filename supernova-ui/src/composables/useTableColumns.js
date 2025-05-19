import { ref, computed } from 'vue'

/**
 * Composable for generating Quasar table columns from data objects
 * @param {Ref} dataSource - Reactive reference to an array of objects
 * @returns {Object} - Collection of table-related composable functions and properties
 */
export function useTableColumns(dataSource, options = {}) {
  const {
    formatter = defaultFormatter
  } = options

  // Default formatter that converts snake_case to Title Case
  function defaultFormatter(fieldName) {
    const spaceCase = fieldName.replace(/_/g, " ").replace("id", "")
    return spaceCase.split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  // Computed columns based on the first item in the data source
  const columns = computed(() => {
    if (!dataSource.value || dataSource.value.length === 0) return []

    const firstItem = dataSource.value[0]
    return Object.keys(firstItem)
      .map(field => {
        // Start with default column definition
        const defaultColumn = {
          name: field,
          label: formatter(field),
          field: field,
          align: 'left',
          sortable: true
        }

        // Override with any custom column settings
        return { ...defaultColumn }
      })
  })

  return {
    columns
  }
}