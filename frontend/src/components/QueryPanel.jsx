import { useRef } from 'react';

export default function QueryPanel({ query, setQuery, onQueryChange }) {
    const debounceRef = useRef(null);

    function handleChange(e) {
        const val = e.target.value;
        setQuery(val);

        if (debounceRef.current) clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => {
            if (onQueryChange) onQueryChange(val);
        }, 600);
    }

    return (
        <div className="panel animate-in">
            <div className="panel-header">Query Input</div>
            <input
                id="query-input"
                type="text"
                value={query}
                onChange={handleChange}
                placeholder='Try: "What is the refund policy?"'
            />
            <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                Enter a user query to test the RAG pipeline
            </p>
        </div>
    );
}
