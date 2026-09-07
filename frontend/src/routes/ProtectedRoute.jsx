import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth, ROLE_HOME } from "../context/AuthContext";
import { StatePanel } from "../components/ui";

export default function ProtectedRoute({ roles }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) return <StatePanel loading />;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (roles && !roles.includes(user.role)) return <Navigate to={ROLE_HOME[user.role]} replace />;
  return <Outlet />;
}
