import { PageGuide } from "@/components/common/page-guide";
import { PublicFooter } from "@/components/layout/public-footer";
import { PublicNav } from "@/components/layout/public-nav";

export default function ContactPage() {
  return (
    <div className="page-wrap">
      <PublicNav />
      <main className="page-container space-y-6">
        <PageGuide
          title="Contact"
          description="Use this page to route product questions, bug reports, and data-quality investigations."
          howToUse={[
            "For production issues, include trace_id and failing endpoint path.",
            "For model output issues, attach the query and returned citations.",
            "For onboarding, include your role and target workflow.",
          ]}
        />

        <section className="grid gap-4 md:grid-cols-2">
          <article className="glass rounded-2xl p-5">
            <h2 className="font-display text-2xl text-stone-900">Support Channels</h2>
            <div className="mt-3 space-y-2 text-sm text-stone-700">
              <p><strong>Email:</strong> support@crmind.ai</p>
              <p><strong>Engineering:</strong> eng@crmind.ai</p>
              <p><strong>Status:</strong> status.crmind.ai</p>
            </div>
          </article>

          <article className="glass rounded-2xl p-5">
            <h2 className="font-display text-2xl text-stone-900">What to include</h2>
            <ul className="mt-3 space-y-2 text-sm text-stone-700">
              <li>• Workflow used (`lead_finder`, `research`, etc.)</li>
              <li>• Approximate timestamp and trace id</li>
              <li>• Expected output vs actual output</li>
              <li>• Screenshot of browser console/network errors</li>
            </ul>
          </article>
        </section>
      </main>
      <PublicFooter />
    </div>
  );
}
