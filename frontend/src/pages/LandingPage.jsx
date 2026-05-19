import { Link } from 'react-router-dom';

const features = [
  {
    title: 'Context-Aware Questions',
    description:
      'Generate interview questions based on candidate projects, technologies, and job requirements — not generic templates.',
  },
  {
    title: 'Recruiter Guidance',
    description:
      'Every question includes evaluation intent, difficulty level, and concise explanations to help recruiters conduct more informed technical discussions.',
  },
  {
    title: 'Scenario-Based Evaluation',
    description:
      'Assess practical engineering thinking with production-inspired scenarios and problem-solving questions.',
  },
  {
    title: 'Structured Technical Screening',
    description:
      'Balanced technical and scenario-driven interview flow designed to support meaningful recruiter-candidate conversations.',
  },
];

export default function LandingPage() {
  return (
    <div className="bg-hero-gradient dark:bg-hero-gradient-dark">
      <section className="mx-auto max-w-6xl px-6 pb-24 pt-20 text-center md:pt-28">
        <p className="section-label mb-5 inline-block rounded-full border border-accent/20 bg-accent-soft/60 px-4 py-1.5 dark:border-accent/30 dark:bg-accent/10">
          AI Interview Intelligence
        </p>
        <h1 className="mx-auto max-w-4xl text-4xl font-bold leading-[1.1] tracking-tight text-ink dark:text-white md:text-6xl md:leading-[1.08]">
          Hire with deeper
          <span className="mt-1 block text-accent dark:text-accent-light">technical insight.</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-ink-muted dark:text-gray-400">
          Upload a candidate resume and job description to generate contextual technical interview
          questions, recruiter guidance, and real-world engineering scenarios tailored to the role and
          candidate profile.
        </p>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link to="/upload" className="btn-primary text-base">
            Open Workspace
          </Link>
        </div>
      </section>

      <section id="features" className="mx-auto max-w-6xl px-6 pb-24">
        <div className="grid gap-5 sm:grid-cols-2">
          {features.map((f) => (
            <div key={f.title} className="card text-left">
              <h3 className="text-lg font-semibold text-ink dark:text-white">{f.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink-muted dark:text-gray-400">
                {f.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-6 pb-32 text-center">
        <div className="rounded-3xl border border-cream-dark bg-white/80 p-10 shadow-soft backdrop-blur-sm transition-all duration-300 ease-smooth hover:shadow-soft-lg dark:border-surface-border dark:bg-surface-card/60">
          <h2 className="text-2xl font-semibold tracking-tight text-ink dark:text-white">
            Designed for smarter technical interviews
          </h2>
          <p className="mx-auto mt-4 max-w-2xl leading-relaxed text-ink-muted dark:text-gray-400">
            Interview Intelligence helps recruiters understand what to ask, why it matters, and how to
            evaluate responses with greater confidence using contextual AI intelligence.
          </p>
          <Link to="/upload" className="btn-primary mt-8 inline-flex">
            Open Workspace
          </Link>
        </div>
      </section>
    </div>
  );
}
