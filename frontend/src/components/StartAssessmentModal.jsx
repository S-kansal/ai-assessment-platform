import { useEffect, useRef, useState } from 'react';

import { createAssessment, startAssessment } from '../services/api.js';

const DEFAULT_TITLE = 'RAG Debugging Assessment';

export default function StartAssessmentModal({ candidate, isOpen, onClose, onSuccess }) {
  const [title, setTitle] = useState(DEFAULT_TITLE);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const modalRef = useRef(null);

  useEffect(() => {
    if (!isOpen) {
      setTitle(DEFAULT_TITLE);
      setError('');
      setIsSubmitting(false);
      return;
    }

    const modalNode = modalRef.current;
    const focusable = modalNode?.querySelectorAll(
      'button:not([disabled]), input:not([disabled])'
    );
    focusable?.[0]?.focus();

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
        return;
      }

      if (event.key !== 'Tab' || !focusable?.length) {
        return;
      }

      const firstElement = focusable[0];
      const lastElement = focusable[focusable.length - 1];

      if (event.shiftKey && document.activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      } else if (!event.shiftKey && document.activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    }

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !candidate) {
    return null;
  }

  function resetAndClose() {
    setTitle(DEFAULT_TITLE);
    setError('');
    setIsSubmitting(false);
    onClose();
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);

    let assessment;
    try {
      assessment = await createAssessment({
        candidate_id: candidate.id,
        title: title.trim() || DEFAULT_TITLE,
      });
    } catch (requestError) {
      setError(`Failed to create assessment: ${requestError.message || 'Unknown error'}`);
      setIsSubmitting(false);
      return;
    }

    const assessmentId = assessment.id ?? assessment.assessment_id ?? assessment.data?.id ?? assessment.data?.assessment_id;
    if (!assessmentId) {
      setError('Failed to create assessment: response did not include an assessment id.');
      setIsSubmitting(false);
      return;
    }

    try {
      const started = await startAssessment(assessmentId);
      onSuccess({
        assessmentId,
        taskRunId: started.task_run_id,
        status: started.status ?? assessment.status ?? 'active',
        title: title.trim() || DEFAULT_TITLE,
      });
      resetAndClose();
    } catch (requestError) {
      setError(`Assessment created but failed to start: ${requestError.message || 'Unknown error'}`);
      setIsSubmitting(false);
    }
  }

  return (
    <div className="modal-overlay" role="presentation">
      <div
        ref={modalRef}
        className="modal-card"
        aria-modal="true"
        aria-labelledby="start-assessment-title"
        role="dialog"
      >
        <div className="stack">
          <div>
            <p className="panel-kicker">Admin Action</p>
            <h2 id="start-assessment-title">Start Assessment for {candidate.name}</h2>
          </div>

          {error ? <p className="error-banner">{error}</p> : null}

          <form className="stack" onSubmit={handleSubmit}>
            <label className="stack">
              <span>Assessment Title</span>
              <input
                required
                type="text"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
              />
            </label>

            <div className="modal-actions">
              <button className="secondary-button" disabled={isSubmitting} onClick={resetAndClose} type="button">
                Cancel
              </button>
              <button className="primary-button" disabled={isSubmitting} type="submit">
                {isSubmitting ? 'Creating...' : 'Create and Start Assessment'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
