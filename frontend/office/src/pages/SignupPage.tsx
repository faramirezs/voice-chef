import { SignupForm } from "@/components/signup-form"
import { Toaster } from "@/components/ui/sonner"
import { Link } from "react-router-dom"

export function SignupPage() {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center bg-muted p-6 md:p-10">
      <div className="w-full max-w-sm md:max-w-4xl">
        <SignupForm />
      </div>
      <Toaster
        position="top-center"
        richColors={true} // This flag tells the library: "Use color schemes for different types (success, error)."
        toastOptions={{
        classNames: {
          title: 'font-semibold',
          description: 'text-black',
        },
      }}
      />
      <div className="mt-4 text-sm text-center text-muted-foreground">
        <Link to="/terms" className="underline hover:text-primary">Terms</Link>
        <span className="mx-2">•</span>
        <Link to="/privacy" className="underline hover:text-primary">Privacy</Link>
      </div>
    </div>
  )
}