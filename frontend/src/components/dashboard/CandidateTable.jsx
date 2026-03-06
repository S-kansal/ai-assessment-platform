import { useNavigate } from 'react-router-dom';

export default function CandidateTable({ candidates }) {
    const navigate = useNavigate();

    if (!candidates || candidates.length === 0) {
        return (
            <div className="panel">
                <div className="panel-header">Candidates</div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>No candidates found.</p>
            </div>
        );
    }

    return (
        <div className="panel animate-in">
            <div className="panel-header">Candidates</div>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--border)' }}>
                            <th className="table-th">Name</th>
                            <th className="table-th">Email</th>
                            <th className="table-th" style={{ textAlign: 'right' }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {candidates.map((c) => (
                            <tr
                                key={c.id}
                                className="table-row"
                                onClick={() => navigate(`/dashboard/candidate/${c.id}`)}
                                style={{ cursor: 'pointer' }}
                            >
                                <td className="table-td">{c.name}</td>
                                <td className="table-td" style={{ color: 'var(--text-secondary)' }}>{c.email}</td>
                                <td className="table-td" style={{ textAlign: 'right' }}>
                                    <span style={{ fontSize: '0.75rem', color: 'var(--accent)' }}>View Report →</span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
