import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function LoginPage() {
    const navigate = useNavigate();
    const { login } = useAuth();

    const [mode, setMode] = useState('login'); // login | register
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [companyName, setCompanyName] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    async function handleLogin(e) {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const { data } = await api.post('/auth/login', { email, password });
            login(data.access_token, {
                userId: data.user_id,
                organizationId: data.organization_id,
                role: data.role,
                email,
            });
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed');
        }
        setLoading(false);
    }

    async function handleRegister(e) {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await api.post('/org/register', {
                company_name: companyName,
                admin_email: email,
                password,
            });
            setSuccess('Organization registered! Logging in...');
            // Auto-login
            const { data } = await api.post('/auth/login', { email, password });
            login(data.access_token, {
                userId: data.user_id,
                organizationId: data.organization_id,
                role: data.role,
                email,
            });
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed');
        }
        setLoading(false);
    }

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem',
        }}>
            <div style={{
                maxWidth: '420px',
                width: '100%',
            }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🏢</div>
                    <h1 style={{
                        fontSize: '1.4rem',
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #38bdf8, #818cf8)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                    }}>
                        AI Assessment Platform
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                        {mode === 'login' ? 'Sign in to your organization' : 'Register your organization'}
                    </p>
                </div>

                {/* Toggle */}
                <div style={{
                    display: 'flex',
                    gap: '0.25rem',
                    background: 'var(--bg-primary)',
                    borderRadius: '0.5rem',
                    padding: '0.25rem',
                    marginBottom: '1.5rem',
                }}>
                    {['login', 'register'].map(m => (
                        <button
                            key={m}
                            onClick={() => { setMode(m); setError(''); setSuccess(''); }}
                            style={{
                                flex: 1,
                                padding: '0.5rem',
                                border: 'none',
                                borderRadius: '0.35rem',
                                cursor: 'pointer',
                                fontSize: '0.85rem',
                                fontWeight: 600,
                                background: mode === m ? 'var(--accent)' : 'transparent',
                                color: mode === m ? '#000' : 'var(--text-secondary)',
                                transition: 'all 0.2s ease',
                            }}
                        >
                            {m === 'login' ? 'Sign In' : 'Register'}
                        </button>
                    ))}
                </div>

                <form onSubmit={mode === 'login' ? handleLogin : handleRegister}>
                    <div className="panel" style={{ padding: '1.5rem' }}>
                        {mode === 'register' && (
                            <div style={{ marginBottom: '1rem' }}>
                                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                                    Company Name
                                </label>
                                <input
                                    type="text"
                                    value={companyName}
                                    onChange={e => setCompanyName(e.target.value)}
                                    placeholder="Acme Corp"
                                    required
                                    style={{
                                        width: '100%',
                                        padding: '0.65rem 0.75rem',
                                        background: 'var(--bg-primary)',
                                        border: '1px solid var(--border)',
                                        borderRadius: '0.35rem',
                                        color: 'var(--text-primary)',
                                        fontSize: '0.9rem',
                                        outline: 'none',
                                        boxSizing: 'border-box',
                                    }}
                                />
                            </div>
                        )}

                        <div style={{ marginBottom: '1rem' }}>
                            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                                Email
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                placeholder="admin@company.com"
                                required
                                style={{
                                    width: '100%',
                                    padding: '0.65rem 0.75rem',
                                    background: 'var(--bg-primary)',
                                    border: '1px solid var(--border)',
                                    borderRadius: '0.35rem',
                                    color: 'var(--text-primary)',
                                    fontSize: '0.9rem',
                                    outline: 'none',
                                    boxSizing: 'border-box',
                                }}
                            />
                        </div>

                        <div style={{ marginBottom: '1.5rem' }}>
                            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.35rem', display: 'block' }}>
                                Password
                            </label>
                            <input
                                type="password"
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                                style={{
                                    width: '100%',
                                    padding: '0.65rem 0.75rem',
                                    background: 'var(--bg-primary)',
                                    border: '1px solid var(--border)',
                                    borderRadius: '0.35rem',
                                    color: 'var(--text-primary)',
                                    fontSize: '0.9rem',
                                    outline: 'none',
                                    boxSizing: 'border-box',
                                }}
                            />
                        </div>

                        {error && (
                            <div style={{
                                background: 'rgba(248,113,113,.1)',
                                border: '1px solid var(--error)',
                                borderRadius: '0.35rem',
                                padding: '0.5rem 0.75rem',
                                marginBottom: '1rem',
                                fontSize: '0.8rem',
                                color: 'var(--error)',
                            }}>
                                ⚠ {error}
                            </div>
                        )}

                        {success && (
                            <div style={{
                                background: 'rgba(52,211,153,.1)',
                                border: '1px solid var(--success)',
                                borderRadius: '0.35rem',
                                padding: '0.5rem 0.75rem',
                                marginBottom: '1rem',
                                fontSize: '0.8rem',
                                color: 'var(--success)',
                            }}>
                                ✓ {success}
                            </div>
                        )}

                        <button
                            type="submit"
                            className="btn-primary"
                            disabled={loading}
                            style={{ width: '100%', fontSize: '0.9rem', padding: '0.65rem' }}
                        >
                            {loading ? 'Please wait…' : mode === 'login' ? 'Sign In' : 'Create Organization'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
