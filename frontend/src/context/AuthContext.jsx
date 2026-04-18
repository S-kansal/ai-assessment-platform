import { useEffect, useMemo, useState } from 'react';

import { AuthContext } from './auth-context.js';
import { registerUnauthorizedHandler, setAuthToken } from '../services/api.js';

function decodeToken(token) {
  if (!token) {
    return null;
  }

  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return {
      userId: payload.sub,
      organizationId: payload.organization_id,
      role: payload.role,
      candidateId: payload.candidate_id,
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
  }, []);

  const value = useMemo(
    () => ({
      token,
      user,
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
