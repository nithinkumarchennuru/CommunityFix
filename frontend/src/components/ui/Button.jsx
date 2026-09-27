export default function Button({ children, variant = 'primary', className = '', type = 'button', ...props }) {
  const variants = {
    primary: 'bg-slate-900 text-white hover:bg-slate-700',
    secondary: 'bg-slate-100 text-slate-900 hover:bg-slate-200',
    success: 'bg-emerald-600 text-white hover:bg-emerald-500',
    danger: 'bg-rose-600 text-white hover:bg-rose-500',
  }

  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium transition-colors ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
