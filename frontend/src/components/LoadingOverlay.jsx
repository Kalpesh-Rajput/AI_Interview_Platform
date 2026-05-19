const STEPS = [
  'Parsing job description & resume',
  'Extracting technical context',
  'Generating contextual questions',
  'Writing recruiter explanations',
  'Supervisor quality validation',
];

export default function LoadingOverlay({ active }) {
  if (!active) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-surface/90 backdrop-blur-sm">
      <div className="mx-4 max-w-md rounded-2xl border border-surface-border bg-surface-card p-8 text-center shadow-2xl">
        <div className="mx-auto mb-6 h-12 w-12 animate-spin rounded-full border-2 border-accent border-t-transparent" />
        <h3 className="text-lg font-semibold text-white">Generating Interview Questions</h3>
        <p className="mt-2 text-sm text-gray-400">
          Our AI agents are analyzing documents and crafting contextual questions...
        </p>
        <ul className="mt-6 space-y-2 text-left text-sm text-gray-500">
          {STEPS.map((step, i) => (
            <li key={step} className="flex items-center gap-2">
              <span className="h-1.5 w-1.5 rounded-full bg-accent/60" style={{ animationDelay: `${i * 0.2}s` }} />
              {step}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
