import type { AssetTypeConfig } from '../../types/asset'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs'
import { AssetCrudPage } from './AssetCrudPage'

export function HoldingsTransactionsTabs({
  holdingsConfig,
  transactionsConfig,
  activeProfileId,
  pageTitle,
}: {
  holdingsConfig: AssetTypeConfig
  transactionsConfig: AssetTypeConfig
  activeProfileId: number | null
  pageTitle: string
}) {
  return (
    <div>
      <h1 className="mb-4 text-2xl font-semibold tracking-tight">{pageTitle}</h1>
      <Tabs defaultValue="holdings">
        <TabsList>
          <TabsTrigger value="holdings">Holdings</TabsTrigger>
          <TabsTrigger value="transactions">Transactions</TabsTrigger>
        </TabsList>
        <TabsContent value="holdings">
          <AssetCrudPage config={holdingsConfig} activeProfileId={activeProfileId} title="Holdings" />
        </TabsContent>
        <TabsContent value="transactions">
          <AssetCrudPage config={transactionsConfig} activeProfileId={activeProfileId} title="Transactions" />
        </TabsContent>
      </Tabs>
    </div>
  )
}
