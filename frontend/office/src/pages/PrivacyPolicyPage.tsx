
export function PrivacyPolicyPage() {
  return (
    <div className="flex min-h-svh items-center justify-center bg-muted p-6 md:p-10">
      <div className="w-full max-w-5xl overflow-hidden rounded-3xl border bg-background shadow-lg">
        <div className="p-8 md:p-12">
          <h1 className="text-2xl font-bold">Privacy Policy</h1>
          <p className="mt-2 text-sm text-muted-foreground">Last updated: May 6, 2026</p>

          <div className="mt-6 space-y-4 prose prose-slate max-w-none">
            <p>
              This Privacy Policy explains how Voice Chef ("we", "us", or "our") collects,
              uses, discloses, and protects personal information when you use our Service.
            </p>

            <h2>1. Information We Collect</h2>
            <ul>
              <li>
                <strong>Information you provide:</strong> account registration details (name,
                email), profile information, User Content (photos, comments, audio clips), and
                communications with us.
              </li>
              <li>
                <strong>Usage information:</strong> logs, device information, IP address,
                analytics data about how you interact with the Service.
              </li>
              <li>
                <strong>Cookies:</strong> Cookies and similar technologies to support features
                and analytics.
              </li>
            </ul>

            <h2>2. How We Use Information</h2>
            <p>
              We use information to: operate and improve the Service; provide and personalize
              features; communicate updates and support; detect and prevent fraud; and comply
              with legal obligations.
            </p>

            <h2>3. Legal Basis (if applicable)</h2>
            <p>
              Where applicable, we process personal data based on user consent, contract
              performance, legitimate interests, or other lawful bases required by local law.
            </p>

            <h2>4. Sharing and Disclosure</h2>
            <p>
              <strong>Service providers:</strong> We may share data with vendors and contractors
              who provide hosting, analytics, payment processing, and other support services
              under contract.
            </p>
            <p>
              <strong>Legal requests:</strong> We may disclose information to comply with legal
              process or protect rights, property, or safety.
            </p>
            <p>
              <strong>Business transfers:</strong> If we merge or are acquired, user information
              may be transferred as part of that transaction.
            </p>

            <h2>5. Third-Party Services and Analytics</h2>
            <p>
                We use third-party services to provide core functionality of the Service, 
                including AI-based features, speech-to-text processing, and analytics.

                When you use these features, certain data may be transmitted to third-party 
                providers. This may include user input (text), audio data, and technical 
                metadata required to process requests.

                These third-party services process data on our behalf and only for the 
                purpose of providing the requested functionality. However, we do not 
                fully control their internal data handling practices.

                We recommend reviewing the privacy policies of these providers for more details.
            </p>

            <h2>6. Cookies and Tracking</h2>
            <p>
              We use cookies and similar technologies. You can manage cookies through your
              browser settings; disabling certain cookies may affect functionality.
            </p>

            <h2>7. Data Security</h2>
            <p>
              We use administrative, technical, and physical safeguards to protect personal
              information. No method of transmission or storage is completely secure; we cannot
              guarantee absolute security.
            </p>

            <h2>8. Data Retention</h2>
            <p>
              We retain personal data as long as necessary to provide the Service and for
              legitimate business purposes, subject to legal retention requirements.
            </p>

            <h2>9. Your Rights</h2>
            <p>
              Depending on your jurisdiction, you may have rights to access, correct, delete,
              or port your personal data, and to object to or restrict processing. Contact us
              to exercise your rights.
            </p>

            <h2>10. Children</h2>
            <p>
              The Service is not intended for children under the applicable minimum age. If we
              discover we have collected personal data from a child without parental consent,
              we will take steps to delete it.
            </p>

            <h2>11. International Transfers</h2>
            <p>
              We may transfer personal data across borders to service providers or affiliates.
              We will take steps to ensure appropriate safeguards are in place.
            </p>

            <h2>12. Changes to This Policy</h2>
            <p>
              We may update this Privacy Policy. We will post changes with a new "Last
              updated" date.
            </p>

            <h2>13. Contact</h2>
            <p>
              For privacy questions or to exercise your rights, contact privacy@voicechef.example
              (replace with the correct contact address).
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
