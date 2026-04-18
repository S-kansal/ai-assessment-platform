import { useEffect, useRef, useState } from 'react';

import { createCandidate } from '../services/api.js';

const INITIAL_FORM = { name: '', email: '', password: '' };

export default function CreateCandidateModal({ isOpen, onClose, onSuccess }) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const modalRef = useRef(null);

  useEffect(() => {
    if (!isOpen) {
      setForm(INITIAL_FORM);
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

  if (!isOpen) {
    return null;
  }

  function resetAndClose() {
    setForm(INITIAL_FORM);
    setError('');
    setIsSubmitting(false);
    onClose();
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');

    if (form.password.trim().length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }

    setIsSubmitting(true);
    try {
      const candidate = await createCandidate({
        name: form.name.trim(),
        email: form.email.trim(),
        password: form.password,
      });
      onSuccess(candidate);
      resetAndClose();
    } catch (requestError) {
      setError(requestError.message || 'Unable to create candidate');
      setIsSubmitting(false);
    }
  }

  return (
    <div className="modal-overlay" role="presentation">
      <div
        ref={modalRef}
        className="modal-card"
        aria-modal="true"
        aria-labelledby="create-candidate-title"
        role="dialog"
      >
        <div className="stack">
          <div>
            <p className="panel-kicker">Admin Action</p>
            <h2 id="create-candidate-title">Create Candidate</h2>
          </div>

          {error ? <p className="error-banner">{error}</p> : null}

          <form className="stack" onSubmit={handleSubmit}>
            <label className="stack">
              <span>Name</span>
              <input
                required
                type="text"
                value={form.name}
                onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
              />
            </label>

            <label className="stack">
              <span>Email</span>
              <input
                required
                autoComplete="email"
                type="email"
                value={form.email}
                onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
              />
            </label>

            <label className="stack">
              <span>Password</span>
              <input
                required
                autoComplete="new-password"
                minLength={8}
                type="password"
                value={form.password}
                onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
              />
            </label>

            <div className="modal-actions">
              <button className="secondary-button" disabled={isSubmitting} onClick={resetAndClose} type="button">
                Cancel
              </button>
              <button className="primary-button" disabled={isSubmitting} type="submit">
                {isSubmitting ? 'Creating...' : 'Create Candidate'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
