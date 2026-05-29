import { Navigate } from 'react-router-dom';
import QuestionCard from '../components/QuestionCard';
import { useInterview } from '../context/InterviewContext';
import { exportJdAnalysisToPdf } from '../utils/exportPdf';

export default function JDAnalysisPage() {
  const { questions, context, meta, reset } = useInterview();

  if (!context) {
    return <Navigate to="/upload" replace />;
  }

  const technical = questions.filter((q) => q.category === 'technical');

  return (
    <section className="mx-auto max-w-4xl px-6 py-12">
      <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="section-label">Role Intelligence</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-ink dark:text-white">JD Analysis</h1>
          <p className="mt-2 text-ink-muted dark:text-gray-400">
            Extracted requirements and technical baseline for the target role.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button onClick={() => exportJdAnalysisToPdf(context)} className="btn-secondary">
            Export PDF
          </button>
          <button onClick={reset} className="btn-secondary">
            New Analysis
          </button>
        </div>
      </div>

      <div className="mb-10 space-y-8">
        {/* Role Expectation Card */}
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
              <span>Target Seniority:</span>
              <span className="rounded-full bg-accent/10 px-2.5 py-0.5 text-xs text-accent-light dark:bg-accent/20">
                {context.experience_level}
              </span>
            </div>
          )}
        </div>

        {/* Required Skills Box */}
        <div>
          <h3 className="section-label mb-3">Required Skills Baseline</h3>
          <div className="rounded-2xl border border-cream-dark bg-white p-5 shadow-card dark:border-surface-border dark:bg-surface-card">
            <div className="flex flex-wrap gap-1.5">
              {(context.extracted_skills_with_levels || []).map((item, idx) => (
                <span
                  key={`skill-${idx}`}
                  className="inline-flex items-center rounded-full bg-accent/[0.06] px-3.5 py-1 text-xs font-semibold text-accent dark:bg-accent-light/10 dark:text-accent-light border border-accent/20 dark:border-accent-light/10"
                >
                  {item.skill}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Screening Questions */}
        {context.self_rating_questions && context.self_rating_questions.length > 0 && (
          <div>
            <h3 className="section-label mb-4">Recruiter Screening Questions</h3>
            <div className="space-y-3">
              {context.self_rating_questions.map((q, idx) => (
                <div key={`rating-q-${idx}`} className="flex items-start justify-between gap-4 rounded-2xl border border-cream-dark bg-white p-4 shadow-card hover:border-accent/20 dark:border-surface-border dark:bg-surface-card">
                  <div className="flex gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent/10 text-xs font-bold text-accent-light mt-0.5">
                      {idx + 1}
                    </span>
                    <p className="text-sm font-medium text-ink dark:text-gray-200 mt-1">{q}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

    </section>
  );
}
