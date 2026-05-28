import { useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import QuestionCard from '../components/QuestionCard';
import { useInterview } from '../context/InterviewContext';
import { exportQuestionsToPdf } from '../utils/exportPdf';

export default function QuestionsPage() {
  const { questions, notes, setNotes, meta, context, reset } = useInterview();
  const [copiedIndex, setCopiedIndex] = useState(null);

  if (!questions?.length && !context) {
    return <Navigate to="/upload" replace />;
  }

  const technical = questions.filter((q) => q.category === 'technical');
  const scenario = questions.filter((q) => q.category === 'scenario');

  const handleNoteChange = (index, value) => {
    setNotes((prev) => ({ ...prev, [index]: value }));
  };

  const handleExport = () => {
    exportQuestionsToPdf(questions, notes, meta, context);
  };

  const copyRatingQuestion = async (text, index) => {
    await navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
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
        <div className="mb-10 space-y-8">
          {/* HR Overview Card */}
          <div className="card border-accent/20 bg-accent/5 dark:bg-accent/5">
            <h2 className="text-lg font-bold text-accent dark:text-accent-light flex items-center gap-2">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Role Expectation Overview
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-ink-muted dark:text-gray-300">
              {context.jd_explanation_for_hr || context.jd_summary || "No description available."}
            </p>
            {context.experience_level && (
              <div className="mt-3 flex items-center gap-2 text-xs font-semibold text-ink-muted dark:text-gray-400">
                <span>Role Seniority Level:</span>
                <span className="rounded-full bg-accent/10 px-2.5 py-0.5 text-xs text-accent-light dark:bg-accent/20">
                  {context.experience_level}
                </span>
              </div>
            )}
          </div>

          {/* Required Skills Box */}
          <div>
            <h3 className="section-label mb-3">Required Skills from JD</h3>
            <div className="rounded-2xl border border-cream-dark bg-white p-4 shadow-card dark:border-surface-border dark:bg-surface-card">
              <div className="flex flex-wrap gap-2">
                {(context.extracted_skills_with_levels || []).map((item, idx) => (
                  <span
                    key={`skill-${idx}`}
                    className="inline-flex items-center rounded-lg bg-accent/10 px-3 py-1.5 text-sm font-semibold text-accent-light dark:bg-accent/20"
                  >
                    {item.skill}
                  </span>
                ))}
                {(!context.extracted_skills_with_levels || context.extracted_skills_with_levels.length === 0) && (
                  <span className="text-sm text-ink-faint">No skills extracted.</span>
                )}
              </div>
            </div>
          </div>

          {/* Self-Rating Questions */}
          {context.self_rating_questions && context.self_rating_questions.length > 0 && (
            <div>
              <h3 className="section-label mb-4">Core Skill Questions</h3>
              <div className="space-y-3">
                {context.self_rating_questions.map((q, idx) => (
                  <div key={`rating-q-${idx}`} className="flex items-start justify-between gap-4 rounded-2xl border border-cream-dark bg-white p-4 shadow-card hover:border-accent/20 dark:border-surface-border dark:bg-surface-card">
                    <div className="flex gap-3">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent/10 text-xs font-bold text-accent-light mt-0.5">
                        {idx + 1}
                      </span>
                      <p className="text-sm font-medium text-ink dark:text-gray-200 mt-1">{q}</p>
                    </div>
                    <button
                      onClick={() => copyRatingQuestion(q, idx)}
                      className="btn-secondary !px-3 !py-1 text-xs shrink-0 self-center"
                    >
                      {copiedIndex === idx ? "Copied!" : "Copy"}
                    </button>
                  </div>
                ))}
              </div>
            </div>
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
