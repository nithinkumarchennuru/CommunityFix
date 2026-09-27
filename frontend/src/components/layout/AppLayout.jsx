import Navbar from './Navbar'
import Sidebar from './Sidebar'

export default function AppLayout({ children }) {
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <Navbar />

      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-5 sm:px-6 lg:flex-row lg:gap-6 lg:px-8 lg:py-6">
        <Sidebar />

        <main className="min-w-0 flex-1 rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200 sm:p-6 lg:rounded-2xl">
          {children}
        </main>
      </div>
    </div>
  )
}
