import { createBrowserRouter, Navigate } from 'react-router'
import Root from './components/Root'
import ConsumerRoot from './components/ConsumerRoot'
import AdminRoot from './components/AdminRoot'

// Public & Auth Pages
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import AdminLogin from './pages/AdminLogin'

// Farmer Pages
import Dashboard from './pages/Dashboard'
import MyProduce from './pages/MyProduce'
import Orders from './pages/Orders'
import OrderDetails from './pages/OrderDetails'
import Verification from './pages/Verification'
import Shipments from './pages/Shipments'
import Forecasts from './pages/Forecasts'
import Profile from './pages/Profile'
import Settings from './pages/Settings'

// Consumer Pages
import ConsumerDashboard from './pages/ConsumerDashboard'
import Marketplace from './pages/Marketplace'
import ProductDetail from './pages/ProductDetail'
import ConsumerCart from './pages/ConsumerCart'
import ConsumerOrders from './pages/ConsumerOrders'
import ConsumerOrderDetail from './pages/ConsumerOrderDetail'
import ConsumerTracking from './pages/ConsumerTracking'
import ConsumerProfile from './pages/ConsumerProfile'

// Admin Pages
import AdminDashboard from './pages/AdminDashboard'
import FarmerVerification from './pages/FarmerVerification'
import FarmerVerificationDetail from './pages/FarmerVerificationDetail'
import AdminDisputes from './pages/AdminDisputes'
import AdminDisputeDetail from './pages/AdminDisputeDetail'
import AdminMonitoring from './pages/AdminMonitoring'
import AdminSettings from './pages/AdminSettings'
import AdminOrders from './pages/AdminOrders'
import AdminListings from './pages/AdminListings'
import AdminUsers from './pages/AdminUsers'

export const router = createBrowserRouter([
  // Public landing & auth
  { path: '/',         Component: Landing },
  { path: '/landing',  Component: Landing },
  { path: '/login',    Component: Login },
  { path: '/register', Component: Register },
  { path: '/admin/login', Component: AdminLogin },

  // Farmer Module
  {
    Component: Root,
    children: [
      { path: '/dashboard',      Component: Dashboard },
      { path: '/produce',        Component: MyProduce },
      { path: '/orders',         Component: Orders },
      { path: '/orders/:id',     Component: OrderDetails },
      { path: '/verification',   Component: Verification },
      { path: '/shipments',      Component: Shipments },
      { path: '/forecasts',      Component: Forecasts },
      { path: '/profile',        Component: Profile },
      { path: '/settings',       Component: Settings },
    ],
  },

  // Consumer Module
  {
    path: '/consumer',
    Component: ConsumerRoot,
    children: [
      { index: true,             Component: ConsumerDashboard },
      { path: 'marketplace',     Component: Marketplace },
      { path: 'marketplace/:id', Component: ProductDetail },
      { path: 'cart',            Component: ConsumerCart },
      { path: 'orders',          Component: ConsumerOrders },
      { path: 'orders/:id',      Component: ConsumerOrderDetail },
      { path: 'tracking',        Component: ConsumerTracking },
      { path: 'profile',         Component: ConsumerProfile },
      { path: 'favourites',      Component: ConsumerProfile },
      { path: 'messages',        Component: ConsumerProfile },
      { path: 'settings',        Component: ConsumerProfile },
    ],
  },

  // Admin Module
  {
    path: '/admin',
    Component: AdminRoot,
    children: [
      { index: true,             Component: AdminDashboard },
      { path: 'verification',     Component: FarmerVerification },
      { path: 'verification/:id', Component: FarmerVerificationDetail },
      { path: 'disputes',         Component: AdminDisputes },
      { path: 'disputes/:id',     Component: AdminDisputeDetail },
      { path: 'users',            Component: AdminUsers },
      { path: 'listings',         Component: AdminListings },
      { path: 'orders',           Component: AdminOrders },
      { path: 'monitoring',       Component: AdminMonitoring },
      { path: 'settings',         Component: AdminSettings },
    ],
  },

  // Fallback redirect
  { path: '*', element: <Navigate to="/" replace /> },
])
