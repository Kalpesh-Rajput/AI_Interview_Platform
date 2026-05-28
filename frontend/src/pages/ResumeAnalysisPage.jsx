import { Navigate } from 'react-router-dom';
import { useInterview } from '../context/InterviewContext';

export default function ResumeAnalysisPage() {
  const { suggestedRoles, reset } = useInterview();

  if (!suggestedRoles) {
    return <Navigate to="/upload" replace />;
  }

  return (
    <section className="mx-auto max-w-5xl px-6 py-12">
      <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="section-label">Candidate Potential</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-ink dark:text-white">Resume Analysis</h1>
          <p className="mt-2 text-ink-muted dark:text-gray-400">
            AI-suggested roles based on last 5 years of experience and skill set.
          </p>
        </div>
        <button onClick={reset} className="btn-secondary">
          New Analysis
        </button>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {suggestedRoles.map((role, idx) => (
          <div
            key={idx}
            className="group relative overflow-hidden rounded-2xl border border-cream-dark bg-white p-6 shadow-card transition-all hover:border-accent/40 hover:shadow-lg dark:border-surface-border dark:bg-surface-card"
          >
            <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-accent/5 blur-2xl group-hover:bg-accent/10" />

            <div className="relative">
              <div className="flex items-center gap-2 mb-4">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-white">
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.184 0-6.22-1.163-8.485-3.125A23.931 23.931 0 013 13.255V4.5c0-1.242 1.008-2.25 2.25-2.25h10.5C18.242 2.25 19.25 3.258 19.25 4.5v8.755z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-ink dark:text-white">
                  {role.role}
                </h3>
              </div>

              <div className="space-y-4">
                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-ink-faint dark:text-gray-500 mb-2">
                    Technical Fit
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {role.technical_skills.split(',').map((skill, sIdx) => (
                      <span
                        key={sIdx}
                        className="rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-ink-muted dark:bg-surface-border dark:text-gray-400"
                      >
                        {skill.trim()}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="text-xs font-bold uppercase tracking-wider text-ink-faint dark:text-gray-500 mb-2">
                    Soft Skill Alignment
                  </p>
                  <p className="text-sm leading-relaxed text-ink-muted dark:text-gray-400">
                    {role.soft_skills}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {suggestedRoles.length === 0 && (
        <div className="text-center py-20">
          <p className="text-ink-muted dark:text-gray-400">No matching roles could be identified from the resume.</p>
        </div>
      )}
    </section>
  );
}
