interface PageGuideProps {
  title: string;
  description: string;
  howToUse: string[];
}

export function PageGuide({ title, description, howToUse }: PageGuideProps) {
  return (
    <section className="glass rounded-2xl p-5">
      <h1 className="font-display text-3xl font-semibold text-stone-900">{title}</h1>
      <p className="mt-2 text-sm text-stone-700">{description}</p>
      <div className="mt-4">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-stone-500">How To Use This Page</h2>
        <ol className="mt-2 grid gap-2 text-sm text-stone-700 md:grid-cols-2">
          {howToUse.map((step, index) => (
            <li key={step} className="rounded-xl border border-stone-300/70 bg-white/70 px-3 py-2">
              <span className="mr-2 font-semibold text-teal-700">{index + 1}.</span>
              {step}
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
