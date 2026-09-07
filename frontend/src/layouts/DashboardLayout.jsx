import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  BadgeCheck, Boxes, ChartNoAxesCombined, CircleDollarSign, ClipboardList,
  Gauge, Handshake, LayoutDashboard, LogOut, Menu, PackageSearch, Route,
  Scale, ShieldCheck, ShoppingBasket, Sprout, Truck, UserRound, X,
} from "lucide-react";
import Logo from "../components/Logo";
import WebMcpTools from "../components/WebMcpTools";
import { useAuth } from "../context/AuthContext";

const roleNames = {
  FARMER: "Farmer",
  CONSUMER: "Consumer",
  BULK_BUYER: "Bulk buyer",
  FINANCIER: "Financier",
  LOGISTICS: "Logistics",
  ADMIN: "Administrator",
};

const navByRole = {
  FARMER: [
    ["Dashboard", "/app/farmer", LayoutDashboard, true], ["My produce", "/app/farmer/produce", Sprout],
    ["Orders", "/app/farmer/orders", ClipboardList], ["Shipments", "/app/farmer/shipments", Truck],
    ["Forecast", "/app/farmer/forecast", ChartNoAxesCombined], ["Verification", "/app/farmer/verification", BadgeCheck],
    ["Profile", "/app/farmer/profile", UserRound],
  ],
  CONSUMER: [
    ["Dashboard", "/app/consumer", LayoutDashboard, true], ["Marketplace", "/app/consumer/marketplace", ShoppingBasket],
    ["Orders", "/app/consumer/orders", ClipboardList], ["Shipments", "/app/consumer/shipments", Truck],
    ["Disputes", "/app/consumer/disputes", Scale], ["Profile", "/app/consumer/profile", UserRound],
  ],
  BULK_BUYER: [
    ["Dashboard", "/app/buyer", LayoutDashboard, true], ["Marketplace", "/app/buyer/marketplace", PackageSearch],
    ["Orders", "/app/buyer/orders", ClipboardList], ["Finance", "/app/buyer/finance", CircleDollarSign],
    ["Profile", "/app/buyer/profile", UserRound],
  ],
  FINANCIER: [
    ["Dashboard", "/app/financier", LayoutDashboard, true], ["Finance requests", "/app/financier/requests", Handshake],
    ["Profile", "/app/financier/profile", UserRound],
  ],
  LOGISTICS: [
    ["Dashboard", "/app/logistics", LayoutDashboard, true], ["Shipments", "/app/logistics/shipments", Truck],
    ["Route optimizer", "/app/logistics/routes", Route],
  ],
  ADMIN: [
    ["Dashboard", "/app/admin", LayoutDashboard, true], ["Verification", "/app/admin/verifications", ShieldCheck],
    ["Disputes", "/app/admin/disputes", Scale], ["Monitoring", "/app/admin/monitoring", Gauge],
    ["Orders", "/app/admin/orders", Boxes],
  ],
};

export default function DashboardLayout() {
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function signOut() {
    logout();
    navigate("/login", { replace: true });
  }

  return <div className="app-shell"><WebMcpTools role={user.role} />
    <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
      <div className="split"><Logo />{menuOpen && <button className="mobile-menu" onClick={() => setMenuOpen(false)} aria-label="Close navigation"><X /></button>}</div>
      <p className="sidebar-role">{roleNames[user.role]} workspace</p>
      <nav className="nav-list" aria-label="Application navigation">
        {navByRole[user.role].map(([label, to, Icon, end]) => <NavLink key={to} end={end} to={to} onClick={() => setMenuOpen(false)} className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}><Icon size={19} /><span>{label}</span></NavLink>)}
      </nav>
      <div className="sidebar-footer"><button className="nav-link" onClick={signOut}><LogOut size={19} />Sign out</button></div>
    </aside>
    <main className="app-main">
      <header className="app-header">
        <button className="mobile-menu" onClick={() => setMenuOpen(true)} aria-label="Open navigation"><Menu /></button>
        <div><strong>{roleNames[user.role]} workspace</strong><div className="muted"><small>Direct market operations</small></div></div>
        <div className="header-user"><div className="avatar">{user.name.charAt(0).toUpperCase()}</div><div><strong>{user.name}</strong><div className="muted"><small>{user.email}</small></div></div></div>
      </header>
      <div className="page-content"><Outlet /></div>
    </main>
  </div>;
}
