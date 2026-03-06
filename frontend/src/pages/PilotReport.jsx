import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function PilotReport() {
    const { token } = useAuth();
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        async function fetchReport() {
            try {
                // Use the JWT token stored in localStorage as the admin key
                const adminToken = localStorage.getItem('jwt_secret') || token;
                const { data } = await api.get(`/pilot/report?token=${adminToken}`);
                setReport(data);
            } catch (err) {
                setError(err.response?.data?.detail || 'Failed to load report. Check your admin token.');
            }
            setLoading(false);
        }
        fetchReport();
    }, [token]);

    if (loading) return <div style={S.page}><p style={S.muted}>Loading pilot report...</p></div>;

    if (error || !report) {
        return (
            <div style={S.page}>
                <div style={S.card}>
                    <h2 style={S.title}>🔒 Pilot Report</h2>
                    <p style={S.error}>{error || 'No report data'}</p>
                    <p style={S.muted}>
                        Set your admin token in localStorage:<br />
                        <code style={S.code}>localStorage.setItem('jwt_secret', 'YOUR_JWT_SECRET')</code>
                    </p>
                </div>
            </div>
        );
    }

    const { summary, participants } = report;

    return (
        <div style={S.page}>
            <div style={{ maxWidth: '1100px', width: '100%' }}>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                    <div>
                        <h1 style={S.title}>📊 Pilot Study Report</h1>
                        <p style={S.muted}>{summary.total_participants} participants · {summary.feedback_responses} feedback responses</p>
                    </div>
                    <div style={S.badge}>ADMIN ONLY</div>
                </div>

                {/* Summary Cards */}
                <div style={S.grid3}>
                    <div style={S.statCard}>
                        <span style={S.statValue}>{summary.total_participants}</span>
                        <span style={S.statLabel}>Participants</span>
                    </div>
                    <div style={S.statCard}>
                        <span style={S.statValue}>{summary.avg_score}</span>
                        <span style={S.statLabel}>Avg Score</span>
                    </div>
                    <div style={S.statCard}>
                        <span style={S.statValue}>{summary.score_range.min} – {summary.score_range.max}</span>
                        <span style={S.statLabel}>Score Range</span>
                    </div>
                </div>

                {/* Feedback Averages */}
                {summary.avg_feedback && Object.keys(summary.avg_feedback).length > 0 && (
                    <div style={{ ...S.card, marginTop: '1.5rem' }}>
                        <h3 style={S.sectionTitle}>📝 Feedback Averages</h3>
                        <div style={S.grid5}>
                            {Object.entries(summary.avg_feedback).map(([key, val]) => (
                                <div key={key} style={S.feedbackItem}>
                                    <span style={S.feedbackVal}>{val || '—'}</span>
                                    <span style={S.feedbackLabel}>{key.replace(/_/g, ' ')}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* By Role */}
                {summary.by_role && Object.keys(summary.by_role).length > 0 && (
                    <div style={{ ...S.card, marginTop: '1.5rem' }}>
                        <h3 style={S.sectionTitle}>👥 Scores by Role</h3>
                        {Object.entries(summary.by_role).map(([role, avg]) => (
                            <div key={role} style={S.roleRow}>
                                <span style={{ color: '#e2e8f0', flex: 1 }}>{role}</span>
                                <div style={{ flex: 2, background: 'rgba(15,23,42,0.8)', borderRadius: '999px', height: '10px', overflow: 'hidden' }}>
                                    <div style={{ width: `${avg}%`, height: '100%', background: 'linear-gradient(90deg, #0ea5e9, #38bdf8)', borderRadius: '999px' }} />
                                </div>
                                <span style={{ color: '#38bdf8', fontWeight: 700, width: '50px', textAlign: 'right' }}>{avg}</span>
                            </div>
                        ))}
                    </div>
                )}

                {/* Participants Table */}
                <div style={{ ...S.card, marginTop: '1.5rem', overflowX: 'auto' }}>
                    <h3 style={S.sectionTitle}>🧑‍💻 Participant Details</h3>
                    <table style={S.table}>
                        <thead>
                            <tr>
                                <th style={S.th}>Name</th>
                                <th style={S.th}>Role</th>
                                <th style={S.th}>Exp</th>
                                <th style={S.th}>LLM Level</th>
                                <th style={S.th}>Score</th>
                                <th style={S.th}>Capabilities</th>
                                <th style={S.th}>Tasks</th>
                                <th style={S.th}>Feedback</th>
                            </tr>
                        </thead>
                        <tbody>
                            {participants.map(p => (
                                <tr key={p.candidate_id} style={S.tr}>
                                    <td style={S.td}>
                                        <div style={{ fontWeight: 600, color: '#e2e8f0' }}>{p.name}</div>
                                        <div style={{ fontSize: '0.7rem', color: '#64748b' }}>{p.email}</div>
                                    </td>
                                    <td style={S.td}>{p.primary_role || '—'}</td>
                                    <td style={S.td}>{p.years_experience != null ? `${p.years_experience}y` : '—'}</td>
                                    <td style={S.td}>
                                        <span style={{
                                            ...S.levelBadge,
                                            background: p.llm_experience_level === 'advanced' ? 'rgba(52,211,153,0.15)' :
                                                p.llm_experience_level === 'intermediate' ? 'rgba(56,189,248,0.15)' : 'rgba(148,163,184,0.15)',
                                            color: p.llm_experience_level === 'advanced' ? '#34d399' :
                                                p.llm_experience_level === 'intermediate' ? '#38bdf8' : '#94a3b8',
                                        }}>
                                            {p.llm_experience_level || '—'}
                                        </span>
                                    </td>
                                    <td style={{ ...S.td, fontWeight: 700, color: p.avg_score >= 80 ? '#34d399' : p.avg_score >= 60 ? '#38bdf8' : '#f87171', fontSize: '1.1rem' }}>
                                        {p.avg_score}
                                    </td>
                                    <td style={S.td}>
                                        {Object.entries(p.capabilities).map(([cap, score]) => (
                                            <div key={cap} style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                                                {cap.replace(/_/g, ' ')}: <span style={{ color: '#38bdf8', fontWeight: 600 }}>{score}</span>
                                            </div>
                                        ))}
                                    </td>
                                    <td style={S.td}>
                                        {p.tasks.map((t, i) => (
                                            <div key={i} style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.2rem' }}>
                                                {t.task_id}: {t.diagnostic_score != null ?
                                                    <span style={{ color: t.diagnostic_score === 1 ? '#34d399' : '#f87171' }}>
                                                        {t.diagnostic_score === 1 ? '✓' : '✗'}
                                                    </span> : '—'}
                                                {t.simulation_runs != null && <span> ({t.simulation_runs} runs)</span>}
                                            </div>
                                        ))}
                                    </td>
                                    <td style={S.td}>
                                        {p.feedback ? (
                                            <div>
                                                <div style={{ fontSize: '0.75rem', color: '#38bdf8' }}>
                                                    ⭐ {p.feedback.overall_experience}/5
                                                </div>
                                                {p.feedback.feedback_text && (
                                                    <div style={{ fontSize: '0.7rem', color: '#64748b', fontStyle: 'italic', marginTop: '0.2rem' }}>
                                                        "{p.feedback.feedback_text}"
                                                    </div>
                                                )}
                                            </div>
                                        ) : <span style={{ color: '#64748b' }}>—</span>}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

const S = {
    page: { minHeight: '100vh', padding: '2rem', background: 'linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0a1628 100%)', display: 'flex', justifyContent: 'center' },
    card: { background: 'rgba(17,24,39,0.9)', border: '1px solid rgba(56,189,248,0.12)', borderRadius: '12px', padding: '1.5rem' },
    title: { color: '#e2e8f0', fontSize: '1.5rem', fontWeight: 700, margin: 0, fontFamily: "'Inter', sans-serif" },
    muted: { color: '#64748b', fontSize: '0.85rem', margin: '0.5rem 0 0' },
    error: { color: '#fca5a5', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '8px', padding: '0.75rem', fontSize: '0.85rem' },
    code: { background: 'rgba(15,23,42,0.8)', padding: '0.3rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', color: '#38bdf8' },
    badge: { background: 'rgba(239,68,68,0.15)', color: '#f87171', fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.1em', padding: '0.3rem 0.8rem', borderRadius: '20px', border: '1px solid rgba(239,68,68,0.3)' },
    grid3: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' },
    grid5: { display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.75rem' },
    statCard: { background: 'rgba(17,24,39,0.9)', border: '1px solid rgba(56,189,248,0.12)', borderRadius: '12px', padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' },
    statValue: { fontSize: '1.8rem', fontWeight: 700, color: '#38bdf8' },
    statLabel: { fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' },
    sectionTitle: { color: '#38bdf8', fontSize: '0.85rem', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '1rem', textTransform: 'uppercase' },
    feedbackItem: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.3rem', padding: '0.75rem', background: 'rgba(15,23,42,0.6)', borderRadius: '8px' },
    feedbackVal: { fontSize: '1.3rem', fontWeight: 700, color: '#38bdf8' },
    feedbackLabel: { fontSize: '0.65rem', color: '#94a3b8', textTransform: 'capitalize', textAlign: 'center' },
    roleRow: { display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem', fontSize: '0.85rem' },
    table: { width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' },
    th: { textAlign: 'left', padding: '0.6rem 0.75rem', color: '#64748b', fontSize: '0.7rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', borderBottom: '1px solid rgba(51,65,85,0.5)' },
    tr: { borderBottom: '1px solid rgba(51,65,85,0.3)' },
    td: { padding: '0.75rem', color: '#94a3b8', verticalAlign: 'top' },
    levelBadge: { fontSize: '0.7rem', fontWeight: 600, padding: '0.2rem 0.5rem', borderRadius: '4px' },
};
