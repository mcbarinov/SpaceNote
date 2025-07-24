import { createBrowserRouter } from "react-router"
import Layout from "./components/layout/Layout"
import LoginPage from "./pages/login"
import IndexPage from "./pages/IndexPage"
import SpaceNotes from "./pages/notes/SpaceNotes"
import NoteDetail from "./pages/notes/NoteDetail"
import { requireAuth } from "./lib/auth"

export const router = createBrowserRouter([
  {
    path: "/login",
    Component: LoginPage,
  },
  {
    path: "/",
    Component: Layout,
    loader: requireAuth,
    children: [
      {
        index: true,
        Component: IndexPage,
      },
      {
        path: "notes/:spaceId",
        Component: SpaceNotes,
      },
      {
        path: "notes/:spaceId/:noteId",
        Component: NoteDetail,
      },
    ],
  },
])
