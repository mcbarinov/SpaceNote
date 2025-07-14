import { useAuthStore } from "../stores/auth"
import { Layout } from "./layout/Layout"
import { UnderConstruction } from "./UnderConstruction"

export function AdminPage() {
  const { user } = useAuthStore()
  const sections = ["Users", "Spaces", "Telegram Bots"]

  return (
    <Layout>
      <section className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">Admin</h2>
        {user && <p className="text-muted-foreground">Welcome, {user.id}!</p>}
      </section>
      
      <section className="grid gap-6 md:grid-cols-3">
        {sections.map(section => (
          <div key={section}>
            <h3 className="text-xl font-semibold mb-4">{section}</h3>
            <UnderConstruction title={section} />
          </div>
        ))}
      </section>
    </Layout>
  )
}