import { Link } from 'react-router-dom';

const features = [
  {
    title: 'Contextual Questions',
    description: 'Questions tailored to JD technologies and resume projects — not generic textbook prompts.',
  },
  {
    title: 'Recruiter-Focused',
    description: 'Every question includes difficulty, technology, and a concise explanation of what it evaluates.',
  },
  {
    title: 'Scenario Deep-Dives',
    description: '3 production-style scenario questions that test real engineering judgment.',
  },
];

export default function LandingPage() {
  return (
    <div className="bg-hero-gradient">
      <section className="mx-auto max-w-6xl px-6 pb-24 pt-20 text-center md:pt-28">
        <p className="mb-4 inline-block rounded-full border border-accent/30 bg-accent/10 px-4 py-1.5 text-xs font-medium uppercase tracking-wider text-accent-light">
          AI Interview Intelligence
        </p>
        <h1 className="mx-auto max-w-3xl text-4xl font-bold leading-tight tracking-tight text-white md:text-6xl">
          Know what to ask.
          <span className="mt-2 block bg-gradient-to-r from-accent-light to-violet-400 bg-clip-text text-transparent">
            Understand why it matters.
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-400">
          Upload a job description and candidate resume. Our multi-agent AI generates 10 contextual
          interview questions — 7 technical and 3 real-world scenarios — with recruiter-friendly explanations.
        </p>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Link to="/upload" className="btn-primary text-base">
            Start Interview Prep
          </Link>
          <a href="#features" className="btn-secondary">
            Learn More
          </a>
        </div>
      </section>

      <section id="features" className="mx-auto max-w-6xl px-6 pb-24">
        <div className="grid gap-6 md:grid-cols-3">
          {features.map((f) => (
            <div key={f.title} className="card text-left">
              <h3 className="text-lg font-semibold text-white">{f.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-gray-400">{f.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-6 pb-32 text-center">
        <div className="rounded-2xl border border-surface-border bg-surface-card/50 p-10">
          <h2 className="text-2xl font-semibold text-white">Built for recruiters, not ATS scoring</h2>
          <p className="mt-4 text-gray-400">
            This platform helps you conduct better technical interviews — not rank or eliminate candidates.
            Focus on meaningful conversations backed by contextual AI intelligence.
          </p>
          <Link to="/upload" className="btn-primary mt-8 inline-flex">
            Open Workspace
          </Link>
        </div>
      </section>
    </div>
  );
}
