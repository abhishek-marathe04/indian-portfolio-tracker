import { QRCodeSVG } from 'qrcode.react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card'

export function WifiQrWidget() {
  const origin = window.location.origin

  return (
    <Card>
      <CardHeader>
        <CardTitle>Open on your phone</CardTitle>
        <CardDescription>
          Scan while on the same Wi-Fi network. Correct once served by the backend at its LAN IP via the daily{' '}
          <code>run.sh</code> flow — this is only cosmetically "wrong" while running <code>npm run dev</code> on the
          Vite port, not worth extra code to handle.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-3">
        <div className="rounded-md bg-white p-3">
          <QRCodeSVG value={origin} size={160} />
        </div>
        <p className="break-all text-sm text-muted-foreground">{origin}</p>
      </CardContent>
    </Card>
  )
}
