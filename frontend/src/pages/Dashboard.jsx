import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import CandidateTable from '../components/dashboard/CandidateTable';
import { listCandidates } from '../services/api';

export default function Dashboard() {
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const { user, logout } = useAuth();

    useEffect(() => {
        listCandidates()
            .then(setCandidates)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    const total = candidates.length;

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h1 style={{
                    fontSize: '1.3rem', fontWeight: 700,
                    background: 'linear-gradient(135deg, #38bdf8, #818cf8)',
                    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                }}>
                    📊 Hiring Manager Dashboard
                </h1>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                    {user && (
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                            {user.email} ({user.role})
                        </span>
                    )}
                    <button className="btn-primary" onClick={() => navigate('/assess')} style={{ fontSize: '0.8rem', padding: '0.45rem 1rem' }}>
                        ← Assessment View
                    </button>
                    <button
                        onClick={() => { logout(); navigate('/login'); }}
                        style={{
                            fontSize: '0.8rem', padding: '0.45rem 1rem',
                            background: 'rgba(248,113,113,.15)',
                            border: '1px solid var(--error)',
                            borderRadius: '0.35rem',
                            color: 'var(--error)',
                            cursor: 'pointer',
                        }}
                    >
                        Logout
                    </button>
                </div>
            </div>

            {/* Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                {[
                    { label: 'Total Candidates', value: total, icon: '👤' },
                    { label: 'Assessments', value: total, icon: '📋' },
                    { label: 'Platform', value: 'Active', icon: '✅' },
                ].map(({ label, value, icon }) => (
                    <div key={label} className="panel animate-in" style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>{icon}</div>
                        <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--accent)' }}>{value}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</div>
                    </div>
                ))}
            </div>

            {/* Candidate table */}
            {loading ? (
                <div className="panel">
                    <p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>Loading candidates…</p>
                </div>
            ) : (
                <CandidateTable candidates={candidates} />
            )}
        </div>
    );
}
