import { useEffect, useMemo, useState } from 'react';

import { AuthContext } from './auth-context.js';
import { registerUnauthorizedHandler, setAuthToken } from '../services/api.js';

function decodeBase64Url(value) {
  const normalized = value.replace(/-/g, '+').replace(/_/g, '/');
  const padding = '='.repeat((4 - (normalized.length % 4)) % 4);
  return window.atob(`${normalized}${padding}`);
}

function decodeToken(token) {
  if (!token) {
    return null;
  }

  try {
    const payload = JSON.parse(decodeBase64Url(token.split('.')[1]));
    return {
      userId: payload.sub,
      organizationId: payload.organization_id,
      organization_id: payload.organization_id,
      role: payload.role,
      candidateId: payload.candidate_id,
      candidate_id: payload.candidate_id,
    };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const user = useMemo(() => decodeToken(token), [token]);

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
    setAuthToken(token);
  }, [token]);

  useEffect(() => {
    registerUnauthorizedHandler(() => setToken(null));

    return () => {
      registerUnauthorizedHandler(null);
    };
  }, []);

  const value = useMemo(
    () => ({
      token,
      user,
      organization_id: user?.organization_id ?? null,
      role: user?.role ?? null,
      isAuthenticated: Boolean(user),
      login(nextToken) {
        setToken(nextToken);
      },
      logout() {
        setToken(null);
      },
    }),
    [token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
