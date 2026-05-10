import type * as React from "react"
import { useState } from "react"
import { isAxiosError } from "axios"
import { Link, useNavigate } from "react-router-dom"
import { HugeiconsIcon } from "@hugeicons/react"
import { ViewIcon, ViewOffSlashIcon } from "@hugeicons/core-free-icons"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { login } from "@/api/auth"
import { saveToken } from "@/hooks/useAuth"

export function LoginForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const navigate = useNavigate()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setErrorMessage(null)
    setIsSubmitting(true)
    const minimumLoaderDelay = new Promise((resolve) => setTimeout(resolve, 2000))

    try {
      const data = await login(email, password)
      await minimumLoaderDelay
      saveToken(data.access_token, data.expires_in)
      localStorage.setItem("user", JSON.stringify(data.user))
      navigate("/", { replace: true })
    } catch (error) {
      await minimumLoaderDelay
      if (isAxiosError<{ detail?: string }>(error)) {
        setErrorMessage(error.response?.data?.detail ?? "Login failed")
      } else {
        setErrorMessage("Login failed")
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle>Login to your account</CardTitle>
          <CardDescription>
            Enter your email below to login to your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin}>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="email">Email</FieldLabel>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="m@example.com"
                  required
                />
              </Field>
              <Field>
                <div className="flex items-center">
                  <FieldLabel htmlFor="password">Password</FieldLabel>
                  <a
                    href="#"
                    className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                  >
                    Forgot your password?
                  </a>
                </div>
                <div className="relative">
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    className="pr-10"
                    required
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-2 inline-flex items-center text-muted-foreground hover:text-foreground"
                    onClick={() => setShowPassword((prev) => !prev)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    <HugeiconsIcon
                      icon={showPassword ? ViewOffSlashIcon : ViewIcon}
                      strokeWidth={2}
                      className="size-4"
                    />
                  </button>
                </div>
              </Field>
              <div className="min-h-5" aria-live="polite">
                {errorMessage ? <FieldError>{errorMessage}</FieldError> : null}
              </div>
              <Field>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Signing in..." : "Login"}
                </Button>
                {isSubmitting ? (
                  <div className="mt-2 flex justify-center" aria-live="polite" aria-label="Signing in">
                    <div className="loader" />
                  </div>
                ) : null}
                <Button variant="outline" type="button">
                  Login with Google
                </Button>
                <FieldDescription className="text-center">
                  Don&apos;t have an account? <Link to="/signup">Sign up</Link>
                </FieldDescription>
              </Field>
            </FieldGroup>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
