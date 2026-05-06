import React from "react";
import personImage from "@/assets/voice-chef-ai.jpg";

export function TermsOfServicePage() {
  return (
    <div className="flex min-h-svh items-center justify-center bg-muted p-6 md:p-10">
      <div className="w-full max-w-5xl overflow-hidden rounded-3xl border bg-background shadow-lg">
        <div className="p-8 md:p-12">
          <h1 className="text-2xl font-bold">Terms of Service</h1>
          <p className="mt-2 text-sm text-muted-foreground">Last updated: May 6, 2026</p>

          <div className="mt-6 space-y-4 prose prose-slate max-w-none">
            <p>
              By accessing or using the services, websites, applications, or other offerings
              provided by Voice Chef ("we", "us", or "our"), you agree to be bound by these
              Terms of Service ("Terms"). If you do not agree to these Terms, do not access or
              use the services.
            </p>

            <h2>1. Description of Service</h2>
            <p>
              We provide voice-driven recipe and cooking assistance, related content, and
              supporting services (the "Service"). The Service may change over time as we add,
              remove, or modify features.
            </p>

            <h2>2. Eligibility</h2>
            <p>
              You must be at least 13 years old (or the minimum age required in your
              jurisdiction) to use the Service. If you are under the required age, do not use the
              Service and ask a parent or guardian for permission.
            </p>

            <h2>3. Accounts and Registration</h2>
            <ul>
              <li>
                You may need to create an account to access certain features. Provide accurate
                information and keep your credentials secure.
              </li>
              <li>You are responsible for activity that occurs under your account.</li>
            </ul>

            <h2>4. User Content</h2>
            <p>
              You may submit content (comments, reviews, photos, audio snippets) to the Service
              ("User Content"). You retain ownership of your User Content but grant us a
              worldwide, royalty-free, transferable license to use, reproduce, and display the
              User Content as necessary to operate and improve the Service.
            </p>

            <h2>5. Acceptable Use</h2>
            <p>
              You agree not to: reverse-engineer or interfere with the Service; attempt to
              access other users' accounts; use the Service to harm others; or otherwise act in
              a way that violates law or these Terms.
            </p>

            <h2>6. Intellectual Property</h2>
            <p>
              All content, trademarks, logos, and materials provided by us are owned or licensed
              by us. Except as expressly permitted, you may not copy, modify, or create
              derivative works.
            </p>

            <h2>7. Third-Party Services</h2>
            <p>
              The Service may include links or integrations with third-party services. We are
              not responsible for third-party content or practices. Use third-party services at
              your own risk.
            </p>

            <h2>8. Privacy</h2>
            <p>
              Our collection and use of personal information is described in our Privacy Policy,
              which is incorporated by reference.
            </p>

            <h2>9. Disclaimers</h2>
            <p>
              The Service is provided "as is" and "as available." We disclaim all warranties to
              the fullest extent permitted by law, including implied warranties of
              merchantability, fitness for a particular purpose, and non-infringement.
            </p>

            <h2>10. Limitation of Liability</h2>
            <p>
              To the maximum extent permitted by law, we and our affiliates will not be liable for
              indirect, incidental, special, consequential, or punitive damages arising from your
              use of the Service.
            </p>

            <h2>11. Indemnification</h2>
            <p>
              You agree to indemnify and hold us harmless from any claims, liabilities, damages,
              losses, or expenses arising out of your breach of these Terms or your use of the
              Service.
            </p>

            <h2>12. Termination</h2>
            <p>
              We may suspend or terminate access to the Service for any reason, including
              violation of these Terms. You may stop using the Service at any time.
            </p>

            <h2>13. Changes to Terms</h2>
            <p>
              We may update these Terms occasionally. We will post the revised Terms with a new
              "Last updated" date. Continued use after changes constitutes acceptance.
            </p>

            <h2>14. Governing Law and Dispute Resolution</h2>
            <p>
              These Terms are governed by the laws of the jurisdiction in which our headquarters
              are located, without regard to conflict-of-law principles. Disputes will be
              resolved in the appropriate courts unless otherwise agreed.
            </p>

            <h2>15. Contact</h2>
            <p>
              If you have questions about these Terms, contact us at privacy@voicechef.example
              (replace with the correct contact address).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
