import { useEffect, useState } from 'react';
import CandidateTable from '../components/dashboard/CandidateTable';
import { listCandidates } from '../services/api';

export default function CandidateList() {
    const [candidates, setCandidates] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        listCandidates()
            .then(setCandidates)
            .catch(() => { })
            .finally(() => setLoading(false));
    }, []);

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent)', marginBottom: '1rem' }}>
                All Candidates
            </h2>
            {loading ? (
                <div className="panel"><p style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>Loading…</p></div>
            ) : (
                <CandidateTable candidates={candidates} />
            )}
        </div>
    );
}
