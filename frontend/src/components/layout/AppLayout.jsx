import Navbar from './Navbar'
import Sidebar from './Sidebar'

export default function AppLayout({ children }) {
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <Navbar />

      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <Sidebar />

        <main className="min-w-0 flex-1 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          {children}
        </main>
      </div>
    </div>
  )
}
