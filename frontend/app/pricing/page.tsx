import { PageGuide } from "@/components/common/page-guide";
import { PublicFooter } from "@/components/layout/public-footer";
import { PublicNav } from "@/components/layout/public-nav";

const PLANS = [
  {
    name: "Starter",
    price: "$0",
    details: "Great for evaluation and interviews",
    includes: ["Entity search", "Basic agent runs", "Saved entities", "API key access"],
  },
  {
    name: "Team",
    price: "$49",
    details: "For active outbound teams",
    includes: ["Higher run limits", "Batch enrichment", "Signal monitoring", "History retention"],
  },
  {
    name: "Enterprise",
    price: "Custom",
    details: "For governed production usage",
    includes: ["Custom SLAs", "Audit exports", "Private deployment options", "Priority support"],
  },
];

export default function PricingPage() {
  return (
    <div className="page-wrap">
      <PublicNav />
      <main className="page-container space-y-6">
        <PageGuide
          title="Pricing"
          description="Choose a plan based on usage intensity, governance requirements, and team size."
          howToUse={[
            "Start with Starter to validate data quality on your real account list.",
            "Move to Team when daily agent runs and enrichment become routine.",
            "Use Enterprise for strict compliance and custom operating constraints.",
          ]}
        />

        <section className="grid gap-4 md:grid-cols-3">
          {PLANS.map((plan) => (
            <article key={plan.name} className="glass rounded-2xl p-5">
              <h2 className="font-display text-2xl text-stone-900">{plan.name}</h2>
              <p className="mt-1 text-3xl font-semibold text-teal-800">{plan.price}</p>
              <p className="mt-2 text-sm text-stone-700">{plan.details}</p>
              <ul className="mt-3 space-y-1 text-sm text-stone-700">
                {plan.includes.map((item) => (
                  <li key={item}>• {item}</li>
                ))}
              </ul>
            </article>
          ))}
        </section>
      </main>
      <PublicFooter />
    </div>
  );
}
