import { useState } from 'react'
import { Link } from 'react-router-dom'

import ErrorMessage from '../../components/common/ErrorMessage'
import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Input from '../../components/ui/Input'
import { createProblem } from '../../services/residentService'

const initialValues = { title: '', description: '', category: '', priority: '', location: '', photo: null }

function validate(values) {
  const errors = {}

  if (!values.title.trim()) errors.title = 'Enter a title for the problem.'
  if (!values.description.trim()) errors.description = 'Describe the problem.'
  if (!values.category.trim()) errors.category = 'Enter a category.'
  if (!values.priority) errors.priority = 'Choose a priority.'
  if (!values.location.trim()) errors.location = 'Enter the problem location.'

  return errors
}

export default function ReportProblemPage() {
  const [values, setValues] = useState(initialValues)
  const [fieldErrors, setFieldErrors] = useState({})
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleChange = (event) => {
    const { name, value, files } = event.target
    setValues((current) => ({ ...current, [name]: files ? files[0] || null : value }))
    setFieldErrors((current) => ({ ...current, [name]: '' }))
    setError('')
    setSuccess(false)
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    const errors = validate(values)
    setFieldErrors(errors)
    setError('')
    setSuccess(false)

    if (Object.keys(errors).length > 0) return

    setLoading(true)

    try {
      await createProblem({ ...values, title: values.title.trim(), description: values.description.trim(), category: values.category.trim(), location: values.location.trim() })
      setValues(initialValues)
      setSuccess(true)
    } catch (submissionError) {
      setError(submissionError.message || 'Unable to submit this problem.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <Link className="text-sm font-semibold text-cyan-800 hover:text-cyan-950" to="/resident">Resident dashboard</Link>
        <p className="mt-5 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-700">Community report</p>
        <h2 className="mt-2 text-3xl font-bold text-slate-950">Report a problem</h2>
        <p className="mt-2 text-sm text-slate-600">Share enough detail to help your community understand the issue.</p>
      </div>

      <Card>
        {error && <div className="mb-5"><ErrorMessage message={error} /></div>}
        {success && <p className="mb-5 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800" role="status">Your report was submitted.</p>}

        <form className="space-y-5" onSubmit={handleSubmit} noValidate>
          <div>
            <Input id="title" name="title" label="Problem title" value={values.title} onChange={handleChange} required aria-invalid={Boolean(fieldErrors.title)} aria-describedby={fieldErrors.title ? 'title-error' : undefined} placeholder="Briefly describe the issue" />
            {fieldErrors.title && <p id="title-error" className="mt-1 text-sm text-rose-700" role="alert">{fieldErrors.title}</p>}
          </div>

          <div className="space-y-2">
            <label htmlFor="description" className="block text-sm font-medium text-slate-700">Description</label>
            <textarea id="description" name="description" rows="5" value={values.description} onChange={handleChange} required aria-invalid={Boolean(fieldErrors.description)} aria-describedby={fieldErrors.description ? 'description-error' : undefined} className="w-full resize-y rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100" placeholder="What is happening, and when did you notice it?" />
            {fieldErrors.description && <p id="description-error" className="text-sm text-rose-700" role="alert">{fieldErrors.description}</p>}
          </div>

          <div className="grid gap-5 sm:grid-cols-2">
            <div>
              <Input id="category" name="category" label="Category" value={values.category} onChange={handleChange} required aria-invalid={Boolean(fieldErrors.category)} aria-describedby={fieldErrors.category ? 'category-error' : undefined} placeholder="For example, roads or lighting" />
              {fieldErrors.category && <p id="category-error" className="mt-1 text-sm text-rose-700" role="alert">{fieldErrors.category}</p>}
            </div>
            <div className="space-y-2">
              <label htmlFor="priority" className="block text-sm font-medium text-slate-700">Priority</label>
              <select id="priority" name="priority" value={values.priority} onChange={handleChange} required aria-invalid={Boolean(fieldErrors.priority)} aria-describedby={fieldErrors.priority ? 'priority-error' : undefined} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:ring-2 focus:ring-cyan-100">
                <option value="">Choose priority</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
              {fieldErrors.priority && <p id="priority-error" className="text-sm text-rose-700" role="alert">{fieldErrors.priority}</p>}
            </div>
          </div>

          <div>
            <Input id="location" name="location" label="Location" value={values.location} onChange={handleChange} required aria-invalid={Boolean(fieldErrors.location)} aria-describedby={fieldErrors.location ? 'location-error' : undefined} placeholder="Street, intersection, or nearby landmark" />
            {fieldErrors.location && <p id="location-error" className="mt-1 text-sm text-rose-700" role="alert">{fieldErrors.location}</p>}
          </div>

          <div className="space-y-2">
            <label htmlFor="photo" className="block text-sm font-medium text-slate-700">Photo <span className="font-normal text-slate-500">(optional)</span></label>
            <input id="photo" name="photo" type="file" accept="image/*" onChange={handleChange} className="block w-full rounded-lg border border-slate-300 bg-white text-sm text-slate-700 file:mr-4 file:border-0 file:bg-slate-100 file:px-4 file:py-2.5 file:font-medium file:text-slate-800 hover:file:bg-slate-200" />
            {values.photo && <p className="text-sm text-slate-600">Selected: {values.photo.name}</p>}
          </div>

          <div className="flex flex-wrap items-center gap-3 border-t border-slate-200 pt-5">
            <Button type="submit" disabled={loading} className="min-w-40">
              {loading ? 'Submitting...' : 'Submit report'}
            </Button>
            <Link className="text-sm font-medium text-slate-600 hover:text-slate-900" to="/resident">Cancel</Link>
          </div>
        </form>
      </Card>
    </div>
  )
}