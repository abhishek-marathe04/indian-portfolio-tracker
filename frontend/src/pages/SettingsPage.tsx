import { PageHeader } from '../components/common/PageHeader'
import { ChangePasswordForm } from '../components/settings/ChangePasswordForm'
import { RefreshPricesButton } from '../components/settings/RefreshPricesButton'
import { WifiQrWidget } from '../components/settings/WifiQrWidget'

export default function SettingsPage() {
  return (
    <div>
      <PageHeader title="Settings" />
      <div className="grid gap-6 lg:grid-cols-2">
        <ChangePasswordForm />
        <RefreshPricesButton />
        <WifiQrWidget />
      </div>
    </div>
  )
}
