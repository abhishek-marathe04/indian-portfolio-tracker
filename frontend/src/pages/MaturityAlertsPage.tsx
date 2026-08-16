import { PageHeader } from '../components/common/PageHeader'
import { MaturityAlertsList } from '../components/maturity/MaturityAlertsList'

export default function MaturityAlertsPage() {
  return (
    <div>
      <PageHeader
        title="Maturity Alerts"
        description="Deposits, provident funds, Sukanya Samriddhi and post office schemes nearing or past maturity."
      />
      <MaturityAlertsList />
    </div>
  )
}
