export default function SolutionSubmit({ solution, setSolution, onSubmit, submitted, loading }) {
    return (
        <div className={`panel animate-in ${submitted ? '' : 'pulse-border'}`}>
            <div className="panel-header">Solution Submission</div>

            {submitted ? (
                <div style={{
                    textAlign: 'center',
                    padding: '1.5rem',
                }}>
                    <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>✅</div>
                    <p style={{ color: 'var(--success)', fontWeight: 600, fontSize: '0.9rem' }}>
                        Solution Submitted
                    </p>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.5rem' }}>
                        Your solution has been recorded and evaluation is in progress.
                    </p>
                </div>
            ) : (
                <>
                    <textarea
                        id="solution-input"
                        rows={4}
                        value={solution}
                        onChange={(e) => setSolution(e.target.value)}
                        placeholder="Describe the root cause and your proposed fix…&#10;&#10;Example: The retrieval system is returning documents based on keyword frequency rather than semantic relevance. Fix: Update the retrieval ranking to use cosine similarity."
                    />
                    <div style={{ marginTop: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                            {solution.length} characters
                        </span>
                        <button
                            id="submit-solution-btn"
                            className="btn-success"
                            onClick={onSubmit}
                            disabled={!solution.trim() || loading}
                        >
                            {loading ? 'Submitting…' : '✓ Submit Solution'}
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}
