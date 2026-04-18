import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import Panel from '../components/Panel.jsx';
import { useAuth } from '../context/useAuth.js';
import { login, registerOrganization } from '../services/api.js';

const initialRegisterState = {
  organization_name: '',
  organization_slug: '',
  admin_email: '',
  admin_password: '',
};

export default function LoginPage() {
  const navigate = useNavigate();
  const { login: storeLogin } = useAuth();
  const [mode, setMode] = useState('login');
  const [loginState, setLoginState] = useState({ email: '', password: '' });
  const [registerState, setRegisterState] = useState(initialRegisterState);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleLogin(event) {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const data = await login(loginState.email, loginState.password);
      storeLogin(data.access_token);
      navigate(data.role === 'candidate' ? '/assessment' : '/dashboard');
    } catch (requestError) {
      setError(requestError.response?.data?.error?.message || 'Unable to sign in');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleRegister(event) {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await registerOrganization(registerState);
      const data = await login(registerState.admin_email, registerState.admin_password);
      storeLogin(data.access_token);
      navigate('/dashboard');
    } catch (requestError) {
      setError(requestError.response?.data?.error?.message || 'Unable to register organization');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="page page-login">
      <div className="hero-copy">
        <p className="eyebrow">AI Engineering Assessment Platform</p>
        <h1>Debugging-first technical assessment for AI system builders.</h1>
        <p className="lede">
          Candidates solve deterministic RAG failures while the platform captures telemetry,
          evaluates diagnostic reasoning, and builds a structured capability profile.
        </p>
      </div>

      <Panel
        title={mode === 'login' ? 'Sign In' : 'Register Organization'}
        actions={
          <div className="mode-toggle">
            <button className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')}>
              Login
            </button>
            <button className={mode === 'register' ? 'active' : ''} onClick={() => setMode('register')}>
              Register
            </button>
          </div>
        }
      >
        {error ? <p className="error-banner">{error}</p> : null}

        {mode === 'login' ? (
          <form className="stack" onSubmit={handleLogin}>
            <label>
              Email
              <input
                value={loginState.email}
                onChange={(event) => setLoginState({ ...loginState, email: event.target.value })}
                type="email"
                autoComplete="username"
                required
              />
            </label>
            <label>
              Password
              <input
                value={loginState.password}
                onChange={(event) => setLoginState({ ...loginState, password: event.target.value })}
                type="password"
                autoComplete="current-password"
                required
              />
            </label>
            <button className="primary-button" disabled={submitting} type="submit">
              {submitting ? 'Signing in...' : 'Sign In'}
            </button>
          </form>
        ) : (
          <form className="stack" onSubmit={handleRegister}>
            <label>
              Organization Name
              <input
                value={registerState.organization_name}
                onChange={(event) =>
                  setRegisterState({ ...registerState, organization_name: event.target.value })
                }
                required
              />
            </label>
            <label>
              Organization Slug
              <input
                value={registerState.organization_slug}
                onChange={(event) =>
                  setRegisterState({ ...registerState, organization_slug: event.target.value })
                }
                required
              />
            </label>
            <label>
              Admin Email
              <input
                value={registerState.admin_email}
                onChange={(event) =>
                  setRegisterState({ ...registerState, admin_email: event.target.value })
                }
                type="email"
                autoComplete="username"
                required
              />
            </label>
            <label>
              Admin Password
              <input
                value={registerState.admin_password}
                onChange={(event) =>
                  setRegisterState({ ...registerState, admin_password: event.target.value })
                }
                type="password"
                autoComplete="new-password"
                required
              />
            </label>
            <button className="primary-button" disabled={submitting} type="submit">
              {submitting ? 'Creating organization...' : 'Create Organization'}
            </button>
          </form>
        )}
      </Panel>
    </main>
  );
}
