export default function DebugLogs({ logs }) {
    if (!logs || logs.length === 0) {
        return (
            <div className="panel" style={{ opacity: 0.5 }}>
                <div className="panel-header">Debug Logs</div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                    No logs yet — run a simulation first
                </p>
            </div>
        );
    }

    function getTagClass(tag) {
        if (tag === 'RETRIEVAL') return 'tag-retrieval';
        if (tag === 'PROMPT') return 'tag-prompt';
        if (tag === 'GENERATION') return 'tag-generation';
        if (tag === 'DEBUG') return 'tag-debug';
        return '';
    }

    function parseLine(line) {
        const match = line.match(/^\[(\w+)]\s*(.*)$/);
        if (match) {
            return { tag: match[1], content: match[2] };
        }
        return { tag: null, content: line };
    }

    return (
        <div className="panel animate-in">
            <div className="panel-header">Debug Logs</div>
            <div style={{ maxHeight: '240px', overflowY: 'auto' }}>
                {logs.map((line, i) => {
                    const { tag, content } = parseLine(line);
                    return (
                        <div key={i} className="log-line">
                            {tag && <span className={`tag ${getTagClass(tag)}`}>[{tag}]</span>}
                            {content}
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
