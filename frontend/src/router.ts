import { createBrowserRouter, redirect } from "react-router"
import Layout from "./components/Layout"
import LoginPage from "./pages/login"
import NotesIndexPage from "./pages/notes"
import SpaceNotes from "./pages/notes/SpaceNotes"
import NoteDetail from "./pages/notes/NoteDetail"

export const router = createBrowserRouter([
  {
    path: "/",
    loader: () => redirect("/notes"),
  },
  {
    path: "/login",
    Component: LoginPage,
  },
  {
    path: "/",
    Component: Layout,
    children: [
      {
        path: "notes",
        Component: NotesIndexPage,
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
