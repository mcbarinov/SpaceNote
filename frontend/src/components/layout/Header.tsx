import { Navigation } from "./Navigation"

export function Header() {
  return (
    <header className="border-b bg-background">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <h1 className="text-2xl font-bold">SpaceNote</h1>
        <Navigation />
      </div>
    </header>
  )
}