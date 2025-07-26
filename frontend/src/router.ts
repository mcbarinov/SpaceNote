import { createBrowserRouter } from "react-router"
import Layout from "./components/layout/Layout"
import LoginPage from "./pages/login"
import IndexPage from "./pages/IndexPage"
import SpaceNotes from "./pages/notes/SpaceNotes"
import CreateNote from "./pages/notes/CreateNote"
import EditNote from "./pages/notes/EditNote"
import NoteDetail from "./pages/notes/NoteDetail"
import SpacesPage from "./pages/spaces"
import SpaceFields from "./pages/spaces/SpaceFields"
import SpaceTemplates from "./pages/spaces/SpaceTemplates"
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
        path: "spaces",
        Component: SpacesPage,
      },
      {
        path: "spaces/:spaceId/fields",
        Component: SpaceFields,
      },
      {
        path: "spaces/:spaceId/templates",
        Component: SpaceTemplates,
      },
      {
        path: "notes/:spaceId",
        Component: SpaceNotes,
      },
      {
        path: "notes/:spaceId/new",
        Component: CreateNote,
      },
      {
        path: "notes/:spaceId/:noteId/edit",
        Component: EditNote,
      },
      {
        path: "notes/:spaceId/:noteId",
        Component: NoteDetail,
      },
    ],
  },
])
