import { useState } from 'react';

const difficultyColors = {
  Easy: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  Medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  Hard: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
};

export default function QuestionCard({ question, index, note, onNoteChange }) {
  const [copied, setCopied] = useState(false);

  const copyQuestion = async () => {
    const text = `Q${index + 1}: ${question.question}\nDifficulty: ${question.difficulty}\nTechnology: ${question.related_technology}\n\n${question.explanation}\n\nAnswer: ${question.answer || ''}`;
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const isScenario = question.category === 'scenario';

  return (
    <article className="card group">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-lg bg-accent/10 px-2.5 py-1 text-xs font-semibold text-accent-light">
            Q{index + 1}
          </span>
          {isScenario && (
            <span className="rounded-lg border border-violet-500/30 bg-violet-500/10 px-2.5 py-1 text-xs font-medium text-violet-300">
              Scenario
            </span>
          )}
          <span
            className={`rounded-lg border px-2.5 py-1 text-xs font-medium ${
              difficultyColors[question.difficulty] || difficultyColors.Medium
            }`}
          >
            {question.difficulty}
          </span>
          <span className="rounded-lg border border-cream-dark bg-cream-muted px-2.5 py-1 text-xs text-ink-muted dark:border-surface-border dark:bg-surface-elevated dark:text-gray-400">
            {question.related_technology}
          </span>
        </div>
        <button
          onClick={copyQuestion}
          className="btn-secondary !px-3 !py-1.5 text-xs opacity-80 transition group-hover:opacity-100"
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>

      <h3 className="text-base font-medium leading-relaxed text-ink dark:text-white md:text-lg">
        {question.question}
      </h3>

      <p className="mt-4 text-sm leading-relaxed text-ink-muted dark:text-gray-400">{question.explanation}</p>

      {question.answer && (
        <div className="mt-4 rounded-md bg-cream-muted/80 p-3 dark:bg-surface-elevated/30">
          <label className="mb-1 block text-xs font-medium uppercase tracking-wider text-ink-faint dark:text-gray-500">
            Answer
          </label>
          <p className="text-sm leading-relaxed text-ink-muted dark:text-gray-300">{question.answer}</p>
        </div>
      )}

      <div className="mt-5 border-t border-cream-dark pt-4 dark:border-surface-border">
        <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-ink-faint dark:text-gray-500">
          Recruiter Notes
        </label>
        <textarea
          value={note || ''}
          onChange={(e) => onNoteChange(index, e.target.value)}
          placeholder="Add interview notes, follow-ups, or observations..."
          rows={2}
          className="w-full resize-none rounded-xl border border-cream-dark bg-white px-4 py-3 text-sm text-ink outline-none transition duration-300 focus:border-accent/50 dark:border-surface-border dark:bg-surface-elevated/50 dark:text-gray-200 dark:placeholder-gray-600"
        />
      </div>
    </article>
  );
}
