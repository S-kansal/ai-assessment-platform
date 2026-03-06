import { useRef } from 'react';

export default function PromptEditor({ promptTemplate, setPromptTemplate, onPromptEdit }) {
    const versionRef = useRef(0);

    function handleChange(e) {
        setPromptTemplate(e.target.value);
        versionRef.current += 1;
        if (onPromptEdit) onPromptEdit(versionRef.current);
    }

    return (
        <div className="panel animate-in">
            <div className="panel-header">Prompt Template</div>
            <textarea
                id="prompt-editor"
                rows={3}
                value={promptTemplate}
                onChange={handleChange}
                placeholder="Use the provided context to answer the question."
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem' }}>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                    Edit the prompt template to control generation behavior
                </span>
                <span style={{ fontSize: '0.7rem', color: 'var(--accent)' }}>
                    v{versionRef.current}
                </span>
            </div>
        </div>
    );
}
