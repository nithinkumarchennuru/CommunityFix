import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Input from '../../components/ui/Input'

export default function RegisterPage() {
  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <Card title="Register" subtitle="Registration flow will be added in a later phase." className="w-full max-w-md">
        <div className="space-y-4">
          <Input id="name" label="Full name" type="text" placeholder="Jane Doe" />
          <Input id="email" label="Email" type="email" placeholder="name@example.com" />
          <Input id="password" label="Password" type="password" placeholder="••••••••" />
          <Button className="w-full" variant="success">Create account</Button>
        </div>
      </Card>
    </div>
  )
}
