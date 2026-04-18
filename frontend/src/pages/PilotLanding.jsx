import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api.js';

const ROLES = [
    'AI/ML Engineer',
    'Backend Engineer',
    'Full-Stack Engineer',
    'Data Scientist',
    'Research Engineer',
    'DevOps / MLOps',
    'Other',
];

const LLM_LEVELS = ['beginner', 'intermediate', 'advanced'];

export default function PilotLanding() {
    const navigate = useNavigate();
    const [step, setStep] = useState('landing'); // landing | register | loading
    const [form, setForm] = useState({
        name: '', email: '', years_experience: '',
        primary_role: '', llm_experience_level: '', company: '',
    });
    const [error, setError] = useState('');

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        setStep('loading');

        try {
            const { data } = await api.post('/pilot/register', {
                ...form,
                years_experience: form.years_experience ? parseInt(form.years_experience) : null,
            });

            // Store candidate info for the assessment
            localStorage.setItem('pilot_candidate_id', data.candidate_id);
            localStorage.setItem('pilot_candidate_name', form.name);
            localStorage.setItem('pilot_candidate_email', form.email);

            navigate('/assess?pilot=true');
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed');
            setStep('register');
        }
    };

    // ── Landing View ──────────────────────────────────
    if (step === 'landing') {
        return (
            <div style={styles.page}>
                <div style={styles.card}>
                    <div style={styles.badge}>🧪 PILOT STUDY</div>
                    <h1 style={styles.title}>AI Engineering<br />Debugging Challenge</h1>
                    <p style={styles.subtitle}>
                        This assessment evaluates how engineers diagnose and fix failures in
                        AI systems — RAG pipelines, LLM prompts, and retrieval workflows.
                    </p>

                    <div style={styles.infoGrid}>
                        <div style={styles.infoItem}>
                            <span style={styles.infoIcon}>🔬</span>
                            <span style={styles.infoLabel}>3 Debugging Tasks</span>
                        </div>
                        <div style={styles.infoItem}>
                            <span style={styles.infoIcon}>⏱️</span>
                            <span style={styles.infoLabel}>45–60 Minutes</span>
                        </div>
                        <div style={styles.infoItem}>
                            <span style={styles.infoIcon}>📊</span>
                            <span style={styles.infoLabel}>Skill Profile Generated</span>
                        </div>
                    </div>

                    <div style={styles.howItWorks}>
                        <h3 style={styles.sectionTitle}>How It Works</h3>
                        <ol style={styles.steps}>
                            <li>You receive a failing AI pipeline scenario</li>
                            <li>Run simulations to diagnose the root cause</li>
                            <li>Inspect retrieval results and prompt behaviour</li>
                            <li>Submit your diagnosis and fix</li>
                        </ol>
                    </div>

                    <button style={styles.ctaButton} onClick={() => setStep('register')}>
                        Start Assessment →
                    </button>

                    <p style={styles.disclaimer}>
                        Your results help improve the platform. All data is confidential.
                    </p>
                </div>
            </div>
        );
    }

    // ── Loading ────────────────────────────────────────
    if (step === 'loading') {
        return (
            <div style={styles.page}>
                <div style={styles.card}>
                    <h2 style={styles.title}>Setting up your assessment...</h2>
                    <div style={styles.spinner} />
                </div>
            </div>
        );
    }

    // ── Registration Form ──────────────────────────────
    return (
        <div style={styles.page}>
            <div style={styles.card}>
                <h2 style={styles.formTitle}>Participant Registration</h2>
                <p style={styles.formSubtitle}>Tell us about yourself before starting.</p>

                {error && <div style={styles.error}>{error}</div>}

                <form onSubmit={handleRegister} style={styles.form}>
                    <label style={styles.label}>
                        NAME *
                        <input style={styles.input} required value={form.name}
                            onChange={e => setForm({ ...form, name: e.target.value })}
                            placeholder="Your full name" />
                    </label>

                    <label style={styles.label}>
                        EMAIL *
                        <input style={styles.input} type="email" required value={form.email}
                            onChange={e => setForm({ ...form, email: e.target.value })}
                            placeholder="you@company.com" />
                    </label>

                    <div style={styles.row}>
                        <label style={{ ...styles.label, flex: 1 }}>
                            YEARS OF EXPERIENCE
                            <input style={styles.input} type="number" min="0" max="40"
                                value={form.years_experience}
                                onChange={e => setForm({ ...form, years_experience: e.target.value })}
                                placeholder="e.g. 5" />
                        </label>
                        <label style={{ ...styles.label, flex: 1 }}>
                            COMPANY
                            <input style={styles.input} value={form.company}
                                onChange={e => setForm({ ...form, company: e.target.value })}
                                placeholder="Optional" />
                        </label>
                    </div>

                    <label style={styles.label}>
                        PRIMARY ROLE
                        <select style={styles.input} value={form.primary_role}
                            onChange={e => setForm({ ...form, primary_role: e.target.value })}>
                            <option value="">Select role...</option>
                            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                        </select>
                    </label>

                    <label style={styles.label}>
                        LLM EXPERIENCE LEVEL
                        <div style={styles.radioGroup}>
                            {LLM_LEVELS.map(l => (
                                <label key={l} style={styles.radioLabel}>
                                    <input type="radio" name="llm_level" value={l}
                                        checked={form.llm_experience_level === l}
                                        onChange={e => setForm({ ...form, llm_experience_level: e.target.value })} />
                                    {l.charAt(0).toUpperCase() + l.slice(1)}
                                </label>
                            ))}
                        </div>
                    </label>

                    <button type="submit" style={styles.ctaButton}>
                        Begin Assessment →
                    </button>

                    <button type="button" style={styles.backButton}
                        onClick={() => setStep('landing')}>
                        ← Back
                    </button>
                </form>
            </div>
        </div>
    );
}

// ── Styles ────────────────────────────────────────────
const styles = {
    page: {
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #0a1628 100%)',
        padding: '2rem',
    },
    card: {
        background: 'rgba(17, 24, 39, 0.9)',
        border: '1px solid rgba(56, 189, 248, 0.15)',
        borderRadius: '16px',
        padding: '3rem',
        maxWidth: '560px',
        width: '100%',
        boxShadow: '0 25px 50px rgba(0,0,0,0.5)',
    },
    badge: {
        display: 'inline-block',
        background: 'rgba(56, 189, 248, 0.1)',
        color: '#38bdf8',
        fontSize: '0.75rem',
        fontWeight: 700,
        letterSpacing: '0.1em',
        padding: '0.4rem 1rem',
        borderRadius: '20px',
        border: '1px solid rgba(56, 189, 248, 0.25)',
        marginBottom: '1.5rem',
    },
    title: {
        color: '#e2e8f0',
        fontSize: '2rem',
        fontWeight: 700,
        lineHeight: 1.2,
        margin: '0 0 1rem',
        fontFamily: "'Inter', sans-serif",
    },
    subtitle: {
        color: '#94a3b8',
        fontSize: '1rem',
        lineHeight: 1.6,
        margin: '0 0 2rem',
    },
    infoGrid: {
        display: 'flex',
        gap: '1rem',
        marginBottom: '2rem',
    },
    infoItem: {
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '1rem 0.5rem',
        background: 'rgba(30, 41, 59, 0.6)',
        borderRadius: '10px',
        border: '1px solid rgba(51, 65, 85, 0.5)',
    },
    infoIcon: { fontSize: '1.5rem' },
    infoLabel: { color: '#cbd5e1', fontSize: '0.8rem', textAlign: 'center', fontWeight: 600 },
    howItWorks: { marginBottom: '2rem' },
    sectionTitle: { color: '#38bdf8', fontSize: '0.9rem', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '0.75rem' },
    steps: { color: '#94a3b8', margin: 0, paddingLeft: '1.2rem', lineHeight: 1.8, fontSize: '0.9rem' },
    ctaButton: {
        width: '100%',
        padding: '0.9rem',
        background: 'linear-gradient(135deg, #0ea5e9, #38bdf8)',
        color: '#0f172a',
        fontWeight: 700,
        fontSize: '1rem',
        border: 'none',
        borderRadius: '10px',
        cursor: 'pointer',
        transition: 'transform 0.15s, box-shadow 0.15s',
        boxShadow: '0 4px 15px rgba(56, 189, 248, 0.3)',
        marginBottom: '1rem',
    },
    disclaimer: { color: '#64748b', fontSize: '0.75rem', textAlign: 'center', margin: 0 },
    formTitle: { color: '#e2e8f0', fontSize: '1.5rem', fontWeight: 700, margin: '0 0 0.5rem' },
    formSubtitle: { color: '#94a3b8', fontSize: '0.9rem', margin: '0 0 1.5rem' },
    form: { display: 'flex', flexDirection: 'column', gap: '1rem' },
    label: { display: 'flex', flexDirection: 'column', gap: '0.4rem', color: '#94a3b8', fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.05em' },
    input: {
        padding: '0.7rem 0.8rem',
        background: 'rgba(15, 23, 42, 0.8)',
        border: '1px solid rgba(51, 65, 85, 0.6)',
        borderRadius: '8px',
        color: '#e2e8f0',
        fontSize: '0.95rem',
        outline: 'none',
    },
    row: { display: 'flex', gap: '1rem' },
    radioGroup: { display: 'flex', gap: '1.5rem', paddingTop: '0.3rem' },
    radioLabel: { color: '#cbd5e1', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' },
    error: { background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', padding: '0.7rem', color: '#fca5a5', fontSize: '0.85rem' },
    backButton: { background: 'none', border: '1px solid rgba(51, 65, 85, 0.5)', borderRadius: '8px', padding: '0.7rem', color: '#94a3b8', cursor: 'pointer', fontSize: '0.9rem' },
    spinner: { width: '40px', height: '40px', border: '3px solid rgba(56,189,248,0.2)', borderTop: '3px solid #38bdf8', borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '2rem auto' },
};
