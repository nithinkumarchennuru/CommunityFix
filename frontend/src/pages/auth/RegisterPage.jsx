import { useState } from 'react'
import { Link } from 'react-router-dom'

import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Input from '../../components/ui/Input'
import { useAuth } from '../../context/useAuth'

function validate(values) {
  const errors = {}

  if (!values.fullName.trim()) {
    errors.fullName = 'Enter your full name.'
  }

  if (!values.email.trim()) {
    errors.email = 'Enter your email address.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) {
    errors.email = 'Enter a valid email address.'
  }

  if (!values.password) {
    errors.password = 'Enter a password.'
  }

  if (!values.confirmPassword) {
    errors.confirmPassword = 'Confirm your password.'
  } else if (values.password !== values.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match.'
  }

  if (!values.role) {
    errors.role = 'Choose an account type.'
  }

  return errors
}

export default function RegisterPage() {
  const { register, loading } = useAuth()
  const [values, setValues] = useState({ fullName: '', email: '', password: '', confirmPassword: '', role: '' })
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
      await register({
        fullName: values.fullName.trim(),
        email: values.email.trim(),
        password: values.password,
        role: values.role,
      })
      setNotice('Your registration request was submitted. You can sign in when your account is ready.')
      setValues({ fullName: '', email: '', password: '', confirmPassword: '', role: '' })
    } catch (error) {
      setFormError(error.message || 'Unable to create your account. Please try again.')
    }
  }

  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <Card title="Create your account" subtitle="Join your local CommunityFix community" className="w-full max-w-md">
        <form className="space-y-5" onSubmit={handleSubmit} noValidate>
          <Input
            id="fullName"
            name="fullName"
            label="Full name"
            type="text"
            autoComplete="name"
            placeholder="Jane Doe"
            value={values.fullName}
            onChange={handleChange}
            required
            aria-invalid={Boolean(fieldErrors.fullName)}
            aria-describedby={fieldErrors.fullName ? 'fullName-error' : undefined}
          />
          {fieldErrors.fullName && <p id="fullName-error" className="-mt-3 text-sm text-rose-700" role="alert">{fieldErrors.fullName}</p>}

          <Input
            id="registerEmail"
            name="email"
            label="Email address"
            type="email"
            autoComplete="email"
            placeholder="name@example.com"
            value={values.email}
            onChange={handleChange}
            required
            aria-invalid={Boolean(fieldErrors.email)}
            aria-describedby={fieldErrors.email ? 'registerEmail-error' : undefined}
          />
          {fieldErrors.email && <p id="registerEmail-error" className="-mt-3 text-sm text-rose-700" role="alert">{fieldErrors.email}</p>}

          <Input
            id="registerPassword"
            name="password"
            label="Password"
            type="password"
            autoComplete="new-password"
            value={values.password}
            onChange={handleChange}
            required
            aria-invalid={Boolean(fieldErrors.password)}
            aria-describedby={fieldErrors.password ? 'registerPassword-error' : undefined}
          />
          {fieldErrors.password && <p id="registerPassword-error" className="-mt-3 text-sm text-rose-700" role="alert">{fieldErrors.password}</p>}

          <Input
            id="confirmPassword"
            name="confirmPassword"
            label="Confirm password"
            type="password"
            autoComplete="new-password"
            value={values.confirmPassword}
            onChange={handleChange}
            required
            aria-invalid={Boolean(fieldErrors.confirmPassword)}
            aria-describedby={fieldErrors.confirmPassword ? 'confirmPassword-error' : undefined}
          />
          {fieldErrors.confirmPassword && <p id="confirmPassword-error" className="-mt-3 text-sm text-rose-700" role="alert">{fieldErrors.confirmPassword}</p>}

          <div className="space-y-2">
            <label htmlFor="role" className="block text-sm font-medium text-slate-700">Account type</label>
            <select
              id="role"
              name="role"
              value={values.role}
              onChange={handleChange}
              required
              aria-invalid={Boolean(fieldErrors.role)}
              aria-describedby={fieldErrors.role ? 'role-error' : undefined}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100"
            >
              <option value="">Select a role</option>
              <option value="resident">Resident</option>
              <option value="worker">Worker</option>
            </select>
            {fieldErrors.role && <p id="role-error" className="text-sm text-rose-700" role="alert">{fieldErrors.role}</p>}
          </div>

          {formError && <p className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-800" role="alert">{formError}</p>}
          {notice && <p className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-800" role="status">{notice}</p>}

          <Button type="submit" className="w-full" variant="success" disabled={loading}>
            {loading ? 'Creating account...' : 'Create account'}
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-600">
          Already have an account? <Link className="font-semibold text-cyan-700 hover:text-cyan-900" to="/login">Sign in</Link>
        </p>
      </Card>
    </div>
  )
}
