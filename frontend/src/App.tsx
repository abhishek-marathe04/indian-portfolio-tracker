import { Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './components/common/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import PerformancePage from './pages/PerformancePage'
import PortfolioLayout from './pages/PortfolioLayout'
import MutualFundsPage from './pages/MutualFundsPage'
import StocksPage from './pages/StocksPage'
import DepositsPage from './pages/DepositsPage'
import ProvidentFundsPage from './pages/ProvidentFundsPage'
import SukanyaSamriddhiPage from './pages/SukanyaSamriddhiPage'
import NpsPage from './pages/NpsPage'
import GoldPage from './pages/GoldPage'
import RealEstatePage from './pages/RealEstatePage'
import InternationalPage from './pages/InternationalPage'
import CryptoPage from './pages/CryptoPage'
import PostOfficePage from './pages/PostOfficePage'
import SavingsAccountsPage from './pages/SavingsAccountsPage'
import GoalsPage from './pages/GoalsPage'
import MaturityAlertsPage from './pages/MaturityAlertsPage'
import UploadCasPage from './pages/UploadCasPage'
import FamilyProfilesPage from './pages/FamilyProfilesPage'
import SettingsPage from './pages/SettingsPage'
import NotFoundPage from './pages/NotFoundPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/performance" element={<PerformancePage />} />

        <Route path="/portfolio" element={<PortfolioLayout />}>
          <Route index element={<Navigate to="mutual-funds" replace />} />
          <Route path="mutual-funds" element={<MutualFundsPage />} />
          <Route path="stocks" element={<StocksPage />} />
          <Route path="deposits" element={<DepositsPage />} />
          <Route path="provident-funds" element={<ProvidentFundsPage />} />
          <Route path="sukanya-samriddhi" element={<SukanyaSamriddhiPage />} />
          <Route path="nps" element={<NpsPage />} />
          <Route path="gold" element={<GoldPage />} />
          <Route path="real-estate" element={<RealEstatePage />} />
          <Route path="international" element={<InternationalPage />} />
          <Route path="crypto" element={<CryptoPage />} />
          <Route path="post-office" element={<PostOfficePage />} />
          <Route path="savings-accounts" element={<SavingsAccountsPage />} />
        </Route>

        <Route path="/goals" element={<GoalsPage />} />
        <Route path="/maturity-alerts" element={<MaturityAlertsPage />} />
        <Route path="/upload-cas" element={<UploadCasPage />} />
        <Route path="/family-profiles" element={<FamilyProfilesPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
