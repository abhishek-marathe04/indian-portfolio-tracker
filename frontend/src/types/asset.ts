export type FieldType = 'text' | 'number' | 'date' | 'datetime' | 'boolean' | 'select' | 'textarea'

export interface FieldOption {
  label: string
  value: string
}

export interface FieldConfig {
  key: string
  label: string
  type: FieldType
  required?: boolean
  options?: FieldOption[]
  defaultValue?: string | number | boolean
  showInTable?: boolean
  format?: 'currency' | 'percent' | 'plain'
  hidden?: boolean
}

export interface AssetRecord {
  id: number
  [key: string]: unknown
}

export interface AssetApi<T extends AssetRecord = AssetRecord> {
  list: (profileId?: number | null) => Promise<T[]>
  create: (data: Record<string, unknown>) => Promise<T>
  update: (id: number, data: Record<string, unknown>) => Promise<T>
  remove: (id: number) => Promise<void>
}

export interface AssetTypeConfig {
  resourcePath: string
  title: string
  singularLabel: string
  api: AssetApi
  fields: FieldConfig[]
}
