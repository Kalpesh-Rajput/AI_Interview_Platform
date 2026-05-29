import { Navigate } from 'react-router-dom';
import { useInterview } from '../context/InterviewContext';
import { exportResumeAnalysisToPdf } from '../utils/exportPdf';

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
        <div className="flex flex-wrap gap-3">
          <button onClick={() => exportResumeAnalysisToPdf(suggestedRoles)} className="btn-secondary">
            Export PDF
          </button>
          <button onClick={reset} className="btn-secondary">
            New Analysis
          </button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {suggestedRoles.map((role, idx) => {
          const matched = role.matched_skills || [];
          const required = role.required_skills || [];

          return (
            <div
              key={idx}
              className="group relative flex flex-col overflow-hidden rounded-3xl border border-cream-dark bg-white p-6 pb-7 shadow-card transition-all duration-300 ease-smooth hover:-translate-y-1 hover:border-accent/30 hover:shadow-soft-lg dark:border-surface-border dark:bg-surface-card"
            >
              {/* Header: Icon and Match score in separate elements on the top row */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent/10 dark:bg-accent-light/10 text-accent dark:text-accent-light transition-all duration-300 group-hover:bg-accent group-hover:text-white group-hover:shadow-soft">
                  <svg className="h-5 w-5 transition-transform duration-300 group-hover:scale-110" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 13.255A23.931 23.931 0 0112 15c-3.184 0-6.22-1.163-8.485-3.125A23.931 23.931 0 013 13.255V4.5c0-1.242 1.008-2.25 2.25-2.25h10.5C18.242 2.25 19.25 3.258 19.25 4.5v8.755z" />
                  </svg>
                </div>
                <div className="inline-flex items-center gap-1.5 rounded-full bg-accent/10 dark:bg-accent-light/10 px-3 py-1 text-xs font-semibold text-accent dark:text-accent-light border border-accent/15 dark:border-accent-light/10">
                  <span className="relative flex h-1.5 w-1.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent dark:bg-accent-light opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-accent dark:bg-accent-light"></span>
                  </span>
                  <span>{role.fit_percentage}% Match</span>
                </div>
              </div>

              {/* Title: Placed below to prevent wrapping & overlap collisions */}
              <h3 className="text-xl font-bold tracking-tight text-ink dark:text-white leading-snug mb-5">
                {role.role}
              </h3>

              {/* Content items */}
              <div className="flex-1 space-y-6">
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <svg className="h-4 w-4 text-accent dark:text-accent-light" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-[11px] font-bold uppercase tracking-wider text-ink-muted/80 dark:text-gray-400">
                      Skill Alignment
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {required.map((skill, sIdx) => {
                      const isMatched = matched.includes(skill);
                      return (
                        <span
                          key={sIdx}
                          className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-medium border transition-all duration-250 ${
                            isMatched
                              ? 'bg-accent/[0.06] text-accent border-accent/25 dark:bg-accent-light/10 dark:text-accent-light dark:border-accent-light/20'
                              : 'bg-black/[0.01] text-ink-faint/80 border-black/[0.06] dark:bg-white/[0.01] dark:text-gray-500 dark:border-white/[0.06]'
                          }`}
                        >
                          {isMatched && (
                            <svg className="mr-1 h-3 w-3 text-accent dark:text-accent-light shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                          {skill}
                        </span>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <svg className="h-4 w-4 text-accent dark:text-accent-light" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-[11px] font-bold uppercase tracking-wider text-ink-muted/80 dark:text-gray-400">
                      Core Competencies
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {role.soft_skills.map((skill, ssIdx) => (
                      <span
                        key={ssIdx}
                        className="inline-flex items-center rounded-full bg-black/[0.02] text-ink-muted/95 dark:bg-white/[0.03] dark:text-gray-300 px-2.5 py-0.5 text-[11px] font-medium border border-black/[0.05] dark:border-white/[0.05]"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Progress bar at the absolute bottom of the card content container */}
              <div className="mt-6 pt-5 border-t border-black/[0.04] dark:border-white/[0.06]">
                <div className="w-full bg-black/[0.03] dark:bg-white/[0.06] h-1.5 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-accent/80 to-accent dark:from-accent-light/80 dark:to-accent-light rounded-full transition-all duration-1000 ease-out"
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
