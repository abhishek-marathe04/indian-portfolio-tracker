import { PageHeader } from '../components/common/PageHeader'
import { SingleUploadForm } from '../components/cas/SingleUploadForm'
import { BulkUploadForm } from '../components/cas/BulkUploadForm'
import { ImportsHistoryTable } from '../components/cas/ImportsHistoryTable'

export default function UploadCasPage() {
  return (
    <div>
      <PageHeader title="Upload CAS" description="Import holdings and transactions from a CAMS/KFintech Consolidated Account Statement." />
      <div className="grid gap-6 lg:grid-cols-2">
        <SingleUploadForm />
        <BulkUploadForm />
      </div>
      <div className="mt-6">
        <ImportsHistoryTable />
      </div>
    </div>
  )
}
