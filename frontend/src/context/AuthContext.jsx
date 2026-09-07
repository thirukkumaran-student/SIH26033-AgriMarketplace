import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getCurrentUser, loginUser, registerUser } from "../api/auth";
import { getToken, setToken } from "../api/client";

const AuthContext = createContext(null);

export const ROLE_HOME = {
  FARMER: "/app/farmer",
  CONSUMER: "/app/consumer",
  BULK_BUYER: "/app/buyer",
  FINANCIER: "/app/financier",
  LOGISTICS: "/app/logistics",
  ADMIN: "/app/admin",
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getToken()));

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    if (!getToken()) {
      setLoading(false);
      return null;
    }
    try {
      const current = await getCurrentUser();
      setUser(current);
      return current;
    } catch {
      logout();
      return null;
    } finally {
      setLoading(false);
    }
  }, [logout]);

  useEffect(() => {
    refreshUser();
    window.addEventListener("agrosave:unauthorized", logout);
    return () => window.removeEventListener("agrosave:unauthorized", logout);
  }, [logout, refreshUser]);

  const login = useCallback(async (credentials) => {
    const result = await loginUser(credentials);
    setToken(result.access_token);
    const current = await getCurrentUser();
    setUser(current);
    return current;
  }, []);

  const register = useCallback((payload) => registerUser(payload), []);

  const value = useMemo(() => ({ user, loading, login, register, logout, refreshUser }), [user, loading, login, register, logout, refreshUser]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
