import { Navigate } from 'react-router-dom';
import { useInterview } from '../context/InterviewContext';

export default function ResumeAnalysisPage() {
  const { suggestedRoles, reset } = useInterview();

  if (!suggestedRoles) {
    return <Navigate to="/upload" replace />;
  }

  return (
    <section className="mx-auto max-w-6xl px-6 py-12">
      <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="section-label">Candidate Potential</p>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-ink dark:text-white">Resume Analysis</h1>
          <p className="mt-2 text-ink-muted dark:text-gray-400">
            Strategic role suggestions based on the last 5 years of professional evidence.
          </p>
        </div>
        <button onClick={reset} className="btn-secondary">
          New Analysis
        </button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {suggestedRoles.map((role, idx) => {
          const matched = role.matched_skills || [];
          const required = role.required_skills || [];

          return (
            <div
              key={idx}
              className="group relative flex flex-col overflow-hidden rounded-3xl border border-cream-dark bg-white p-6 shadow-card transition-all hover:border-accent/40 hover:shadow-lg dark:border-surface-border dark:bg-surface-card"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent text-white shadow-accent/20">
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.184 0-6.22-1.163-8.485-3.125A23.931 23.931 0 013 13.255V4.5c0-1.242 1.008-2.25 2.25-2.25h10.5C18.242 2.25 19.25 3.258 19.25 4.5v8.755z" />
                    </svg>
                  </div>
                  <h3 className="text-xl font-bold text-ink dark:text-white leading-tight">
                    {role.role}
                  </h3>
                </div>
                <div className="relative flex flex-col items-end">
                  <span className="text-lg font-bold text-accent dark:text-accent-light">
                    {role.fit_percentage}%
                  </span>
                  <span className="text-[10px] font-bold uppercase tracking-tighter text-ink-faint dark:text-gray-500">
                    Match
                  </span>
                </div>
              </div>

              <div className="flex-1 space-y-6">
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <svg className="h-4 w-4 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-xs font-bold uppercase tracking-wider text-ink-faint dark:text-gray-500">
                      Skill Alignment
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {required.map((skill, sIdx) => {
                      const isMatched = matched.includes(skill);
                      return (
                        <span
                          key={sIdx}
                          className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-medium transition-colors ${
                            isMatched
                              ? 'bg-emerald-100 text-emerald-700 border border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20'
                              : 'bg-gray-100 text-gray-400 border border-gray-200 dark:bg-surface-border dark:text-gray-600 dark:border-surface-border'
                          }`}
                        >
                          {isMatched && <span className="mr-1 text-[10px]">✓</span>}
                          {skill}
                        </span>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <svg className="h-4 w-4 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-xs font-bold uppercase tracking-wider text-ink-faint dark:text-gray-500">
                      Core Competencies
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {role.soft_skills.map((skill, ssIdx) => (
                      <span
                        key={ssIdx}
                        className="rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-ink-muted dark:bg-surface-border dark:text-gray-400"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-gray-100 dark:border-surface-border">
                 <div className="w-full bg-gray-100 dark:bg-surface-border h-1.5 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-accent rounded-full transition-all duration-500"
                      style={{ width: `${role.fit_percentage}%` }}
                    />
                 </div>
              </div>
            </div>
          );
        })}
      </div>

      {suggestedRoles.length === 0 && (
        <div className="text-center py-20">
          <p className="text-ink-muted dark:text-gray-400">No matching roles could be identified from the resume.</p>
        </div>
      )}
    </section>
  );
}
