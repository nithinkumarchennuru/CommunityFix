import { useState } from 'react'
import { Link } from 'react-router-dom'

import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Input from '../../components/ui/Input'
import { useAuth } from '../../context/useAuth'

function validate(values) {
  const errors = {}

  if (!values.email.trim()) {
    errors.email = 'Enter your email address.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
    errors.email = 'Enter a valid email address.'
  }

  if (!values.password) {
    errors.password = 'Enter your password.'
  }

  return errors
}

export default function LoginPage() {
  const { login, logout, isAuthenticated, loading } = useAuth()
  const [values, setValues] = useState({ email: '', password: '' })
  const [fieldErrors, setFieldErrors] = useState({})
  const [formError, setFormError] = useState('')
  const [notice, setNotice] = useState('')

  const handleChange = (event) => {
    const { name, value } = event.target
    setValues((current) => ({ ...current, [name]: value }))
    setFieldErrors((current) => ({ ...current, [name]: '' }))
    setFormError('')
    setNotice('')
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const errors = validate(values)
    setFieldErrors(errors)
    setFormError('')
    setNotice('')

    if (Object.keys(errors).length > 0) {
      return
    }

    try {
      await login({ email: values.email.trim(), password: values.password })
      setNotice('You are signed in. Your workspace will be available when your account role is provided by the authentication service.')
      setValues({ email: '', password: '' })
    } catch (error) {
      setFormError(error.message || 'Unable to sign in. Please try again.')
    }
  }

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <Card title="Welcome back" subtitle="Sign in to CommunityFix" className="w-full max-w-md">
        <form className="space-y-5" onSubmit={handleSubmit} noValidate>
          <Input
            id="email"
            name="email"
            label="Email address"
            type="email"
            autoComplete="email"
            placeholder="name@example.com"
            value={values.email}
            onChange={handleChange}
            required
            aria-invalid={Boolean(fieldErrors.email)}
            aria-describedby={fieldErrors.email ? 'email-error' : undefined}
          />
          {fieldErrors.email && <p id="email-error" className="-mt-3 text-sm text-rose-700" role="alert">{fieldErrors.email}</p>}

          <Input
            id="password"
            name="password"
            label="Password"
            type="password"
            autoComplete="current-password"
            value={values.password}
            onChange={handleChange}
            required
            aria-invalid={Boolean(fieldErrors.password)}
            aria-describedby={fieldErrors.password ? 'password-error' : undefined}
          />
          {fieldErrors.password && <p id="password-error" className="-mt-3 text-sm text-rose-700" role="alert">{fieldErrors.password}</p>}

          {formError && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-800" role="alert">{formError}</p>}
          {notice && <p className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-800" role="status">{notice}</p>}

          <Button type="submit" className="w-full" disabled={loading || isAuthenticated}>
            {loading ? 'Signing in...' : isAuthenticated ? 'Signed in' : 'Sign in'}
          </Button>
          {isAuthenticated && (
            <Button type="button" variant="secondary" className="w-full" onClick={logout}>
              Sign out
            </Button>
          )}
        </form>

        <p className="mt-6 text-center text-sm text-slate-600">
          New to CommunityFix? <Link className="font-semibold text-cyan-700 hover:text-cyan-900" to="/register">Create an account</Link>
        </p>
      </Card>
    </div>
  )
}
