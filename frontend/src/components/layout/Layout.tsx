import { Outlet } from "react-router"
import Footer from "./Footer"
import Header from "./Header"

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col 	max-w-screen-xl mx-auto">
      <Header />
      <main className="flex-1 p-8">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
