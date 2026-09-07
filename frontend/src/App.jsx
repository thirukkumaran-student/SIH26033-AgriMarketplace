import { Navigate, Route, Routes } from "react-router-dom";
import DashboardLayout from "./layouts/DashboardLayout";
import ProtectedRoute from "./routes/ProtectedRoute";
import { useAuth, ROLE_HOME } from "./context/AuthContext";
import { LandingPage, LoginPage, RegisterPage } from "./pages/PublicPages";
import { AdminDashboard, BuyerDashboard, ConsumerDashboard, FarmerDashboard, FinancierDashboard, LogisticsDashboard } from "./pages/Dashboards";
import { ProduceFormPage, ProduceListPage } from "./pages/ProducePages";
import { MarketplacePage, ProduceDetailPage } from "./pages/MarketplacePages";
import OrdersPage from "./pages/OrdersPage";
import ShipmentsPage from "./pages/ShipmentsPage";
import ForecastPage from "./pages/ForecastPage";
import VerificationPage from "./pages/VerificationPage";
import ProfilePage from "./pages/ProfilePage";
import DisputesPage from "./pages/DisputesPage";
import { BuyerFinancePage, FinancierRequestsPage } from "./pages/FinancePages";
import { LogisticsShipmentDetailPage, LogisticsShipmentsPage, RouteOptimizerPage } from "./pages/LogisticsPages";
import { AdminDisputesPage, AdminMonitoringPage, AdminVerificationsPage } from "./pages/AdminPages";

function RoleHome() {
  const { user, loading } = useAuth();
  if (loading) return null;
  return <Navigate to={user ? ROLE_HOME[user.role] : "/login"} replace />;
}

export default function App() {
  return <Routes>
    <Route path="/" element={<LandingPage />} />
    <Route path="/login" element={<LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />
    <Route path="/app" element={<RoleHome />} />

    <Route element={<ProtectedRoute roles={["FARMER"]} />}><Route path="/app/farmer" element={<DashboardLayout />}>
      <Route index element={<FarmerDashboard />} /><Route path="produce" element={<ProduceListPage />} /><Route path="produce/new" element={<ProduceFormPage />} /><Route path="produce/:id/edit" element={<ProduceFormPage />} /><Route path="orders" element={<OrdersPage />} /><Route path="shipments" element={<ShipmentsPage />} /><Route path="forecast" element={<ForecastPage />} /><Route path="verification" element={<VerificationPage />} /><Route path="profile" element={<ProfilePage />} />
    </Route></Route>

    <Route element={<ProtectedRoute roles={["CONSUMER"]} />}><Route path="/app/consumer" element={<DashboardLayout />}>
      <Route index element={<ConsumerDashboard />} /><Route path="marketplace" element={<MarketplacePage />} /><Route path="marketplace/:id" element={<ProduceDetailPage />} /><Route path="orders" element={<OrdersPage />} /><Route path="shipments" element={<ShipmentsPage />} /><Route path="disputes" element={<DisputesPage />} /><Route path="profile" element={<ProfilePage />} />
    </Route></Route>

    <Route element={<ProtectedRoute roles={["BULK_BUYER"]} />}><Route path="/app/buyer" element={<DashboardLayout />}>
      <Route index element={<BuyerDashboard />} /><Route path="marketplace" element={<MarketplacePage />} /><Route path="marketplace/:id" element={<ProduceDetailPage />} /><Route path="orders" element={<OrdersPage />} /><Route path="finance" element={<BuyerFinancePage />} /><Route path="profile" element={<ProfilePage />} />
    </Route></Route>

    <Route element={<ProtectedRoute roles={["FINANCIER"]} />}><Route path="/app/financier" element={<DashboardLayout />}>
      <Route index element={<FinancierDashboard />} /><Route path="requests" element={<FinancierRequestsPage />} /><Route path="profile" element={<ProfilePage />} />
    </Route></Route>

    <Route element={<ProtectedRoute roles={["LOGISTICS"]} />}><Route path="/app/logistics" element={<DashboardLayout />}>
      <Route index element={<LogisticsDashboard />} /><Route path="shipments" element={<LogisticsShipmentsPage />} /><Route path="shipments/:id" element={<LogisticsShipmentDetailPage />} /><Route path="routes" element={<RouteOptimizerPage />} />
    </Route></Route>

    <Route element={<ProtectedRoute roles={["ADMIN"]} />}><Route path="/app/admin" element={<DashboardLayout />}>
      <Route index element={<AdminDashboard />} /><Route path="verifications" element={<AdminVerificationsPage />} /><Route path="disputes" element={<AdminDisputesPage />} /><Route path="monitoring" element={<AdminMonitoringPage />} /><Route path="orders" element={<OrdersPage />} />
    </Route></Route>

    <Route path="*" element={<RoleHome />} />
  </Routes>;
}
