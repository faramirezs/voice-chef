import { LoginForm } from "@/components/login-form"
import personImage from "@/assets/voice-chef-person.jpg"
import { Link } from "react-router-dom"

export function LoginPage() {
  return (
    <div className="flex min-h-svh items-center justify-center bg-muted p-6 md:p-10">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-3xl border bg-background shadow-lg md:grid-cols-2">
        <div
          className="relative hidden min-h-[420px] bg-cover bg-center bg-no-repeat md:block"
          style={{ backgroundImage: `linear-gradient(rgb(0 0 0 / 0%), rgb(0 0 0 / 0%)), url(${personImage})` }}
        >
          <div className="absolute inset-0 flex flex-col justify-end p-8 text-white">
          </div>
        </div>
        <div className="p-6 md:p-8">
          <LoginForm />
          <div className="mt-4 text-sm text-center text-muted-foreground">
            <Link to="/terms" className="underline hover:text-primary">Terms</Link>
            <span className="mx-2">•</span>
            <Link to="/privacy" className="underline hover:text-primary">Privacy</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
