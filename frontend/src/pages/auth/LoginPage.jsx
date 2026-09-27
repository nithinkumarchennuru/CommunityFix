import Button from '../../components/ui/Button'
import Card from '../../components/ui/Card'
import Input from '../../components/ui/Input'

export default function LoginPage() {
  return (
    <div className="flex min-h-[70vh] items-center justify-center px-4">
      <Card title="Login" subtitle="Authentication will be added in a later phase." className="w-full max-w-md">
        <div className="space-y-4">
          <Input id="email" label="Email" type="email" placeholder="name@example.com" />
          <Input id="password" label="Password" type="password" placeholder="••••••••" />
          <Button className="w-full">Continue</Button>
        </div>
      </Card>
    </div>
  )
}
