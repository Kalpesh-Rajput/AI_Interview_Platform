import { Link, Navigate } from 'react-router-dom';
import QuestionCard from '../components/QuestionCard';
import { useInterview } from '../context/InterviewContext';
import { exportQuestionsToPdf } from '../utils/exportPdf';

export default function QuestionsPage() {
  const { questions, notes, setNotes, meta, context, reset } = useInterview();

  if (!questions?.length) {
    return <Navigate to="/upload" replace />;
  }

  const technical = questions.filter((q) => q.category === 'technical');
  const scenario = questions.filter((q) => q.category === 'scenario');

  const handleNoteChange = (index, value) => {
    setNotes((prev) => ({ ...prev, [index]: value }));
  };

  const handleExport = () => {
    exportQuestionsToPdf(questions, notes, meta);
  };

  return (
    <section className="mx-auto max-w-4xl px-6 py-12">
      <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="section-label">AI Question Workspace</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-ink dark:text-white">Interview Questions</h1>
          <p className="mt-2 text-ink-muted dark:text-gray-400">
            {technical.length} technical · {scenario.length} scenario
            {meta.qualityScore > 0 && (
              <span className="ml-2 text-gray-500">
                · Quality {Math.round(meta.qualityScore * 100)}%
              </span>
            )}
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button onClick={handleExport} className="btn-secondary">
            Export PDF
          </button>
          <button onClick={reset} className="btn-secondary">
            New Session
          </button>
          <Link to="/upload" className="btn-primary">
            Regenerate
          </Link>
        </div>
      </div>

      {context && (
        <div className="card mb-8 text-sm text-ink-muted dark:text-gray-400">
          <p>
            <span className="font-medium text-ink dark:text-gray-300">Stack:</span>{' '}
            {(context.normalized_technologies || context.technical_stack || []).slice(0, 8).join(', ')}
          </p>
          {context.experience_level && (
            <p className="mt-2">
              <span className="font-medium text-ink dark:text-gray-300">Level:</span> {context.experience_level}
            </p>
          )}
        </div>
      )}

      <div className="mb-6">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-ink-faint dark:text-gray-500">
          Technical & Conceptual ({technical.length})
        </h2>
      </div>
      <div className="space-y-6">
        {questions.map((q, i) =>
          q.category === 'technical' ? (
            <QuestionCard
              key={`q-${i}`}
              question={q}
              index={i}
              note={notes[i]}
              onNoteChange={handleNoteChange}
            />
          ) : null
        )}
      </div>

      <div className="mb-6 mt-12">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-ink-faint dark:text-gray-500">
          Scenario Deep Evaluation ({scenario.length})
        </h2>
      </div>
      <div className="space-y-6">
        {questions.map((q, i) =>
          q.category === 'scenario' ? (
            <QuestionCard
              key={`q-${i}`}
              question={q}
              index={i}
              note={notes[i]}
              onNoteChange={handleNoteChange}
            />
          ) : null
        )}
      </div>
    </section>
  );
}
