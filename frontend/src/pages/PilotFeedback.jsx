import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import api from '../services/api';

const QUESTIONS = [
    { key: 'task_realism', label: 'How realistic were the tasks?', emoji: '🎯' },
    { key: 'instruction_clarity', label: 'How clear were the instructions?', emoji: '📋' },
    { key: 'evaluation_fairness', label: 'How fair was the evaluation?', emoji: '⚖️' },
    { key: 'difficulty', label: 'How balanced was the difficulty?', emoji: '📊' },
    { key: 'overall_experience', label: 'Overall experience?', emoji: '⭐' },
];

export default function PilotFeedback() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const candidateId = searchParams.get('candidateId') || localStorage.getItem('pilot_candidate_id');
    const [ratings, setRatings] = useState({});
    const [feedbackText, setFeedbackText] = useState('');
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            await api.post('/pilot/feedback', {
                candidate_id: candidateId,
                ...ratings,
                feedback_text: feedbackText || null,
            });
            setSubmitted(true);
        } catch (err) {
            setError(err.response?.data?.detail || 'Submission failed');
        }
    };

    if (submitted) {
        return (
            <div style={styles.page}>
                <div style={styles.card}>
                    <div style={{ fontSize: '3rem', textAlign: 'center', marginBottom: '1rem' }}>🎉</div>
                    <h2 style={styles.title}>Thank You!</h2>
                    <p style={styles.subtitle}>
                        Your feedback has been recorded. It will help us improve the platform
                        for future engineers.
                    </p>
                    <p style={{ ...styles.subtitle, color: '#38bdf8', fontWeight: 600 }}>
                        Your assessment results are being processed.
                    </p>
                    <button style={styles.ctaButton} onClick={() => navigate('/pilot')}>
                        Back to Home
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div style={styles.page}>
            <div style={styles.card}>
                <h2 style={styles.title}>Assessment Complete!</h2>
                <p style={styles.subtitle}>
                    Help us improve the platform with your feedback.
                    Rate each aspect from 1 (poor) to 5 (excellent).
                </p>

                {error && <div style={styles.error}>{error}</div>}

                <form onSubmit={handleSubmit} style={styles.form}>
                    {QUESTIONS.map(({ key, label, emoji }) => (
                        <div key={key} style={styles.questionRow}>
                            <span style={styles.questionLabel}>{emoji} {label}</span>
                            <div style={styles.ratingGroup}>
                                {[1, 2, 3, 4, 5].map(val => (
                                    <button key={val} type="button"
                                        style={{
                                            ...styles.ratingBtn,
                                            ...(ratings[key] === val ? styles.ratingBtnActive : {}),
                                        }}
                                        onClick={() => setRatings({ ...ratings, [key]: val })}>
                                        {val}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ))}

                    <label style={styles.label}>
                        SUGGESTIONS OR COMMENTS
                        <textarea style={{ ...styles.input, minHeight: '80px', resize: 'vertical' }}
                            value={feedbackText}
                            onChange={e => setFeedbackText(e.target.value)}
                            placeholder="What could we improve?" />
                    </label>

                    <button type="submit" style={styles.ctaButton}>
                        Submit Feedback →
                    </button>
                </form>
            </div>
        </div>
    );
}

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
        padding: '2.5rem',
        maxWidth: '560px',
        width: '100%',
        boxShadow: '0 25px 50px rgba(0,0,0,0.5)',
    },
    title: { color: '#e2e8f0', fontSize: '1.5rem', fontWeight: 700, margin: '0 0 0.5rem', textAlign: 'center' },
    subtitle: { color: '#94a3b8', fontSize: '0.9rem', lineHeight: 1.6, margin: '0 0 1.5rem', textAlign: 'center' },
    form: { display: 'flex', flexDirection: 'column', gap: '1.2rem' },
    questionRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' },
    questionLabel: { color: '#cbd5e1', fontSize: '0.9rem', flex: 1 },
    ratingGroup: { display: 'flex', gap: '0.4rem' },
    ratingBtn: {
        width: '36px', height: '36px',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'rgba(15, 23, 42, 0.8)',
        border: '1px solid rgba(51, 65, 85, 0.6)',
        borderRadius: '8px',
        color: '#94a3b8',
        fontSize: '0.85rem',
        cursor: 'pointer',
        transition: 'all 0.15s',
    },
    ratingBtnActive: {
        background: 'rgba(56, 189, 248, 0.2)',
        border: '1px solid rgba(56, 189, 248, 0.5)',
        color: '#38bdf8',
        fontWeight: 700,
    },
    label: { display: 'flex', flexDirection: 'column', gap: '0.4rem', color: '#94a3b8', fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.05em' },
    input: {
        padding: '0.7rem 0.8rem',
        background: 'rgba(15, 23, 42, 0.8)',
        border: '1px solid rgba(51, 65, 85, 0.6)',
        borderRadius: '8px',
        color: '#e2e8f0',
        fontSize: '0.95rem',
        outline: 'none',
        fontFamily: 'inherit',
    },
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
        boxShadow: '0 4px 15px rgba(56, 189, 248, 0.3)',
        marginTop: '0.5rem',
    },
    error: { background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', padding: '0.7rem', color: '#fca5a5', fontSize: '0.85rem' },
};
