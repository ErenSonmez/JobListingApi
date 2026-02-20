import { createBrowserRouter } from "react-router-dom";
import { Layout } from "@shared/components/layout";
import { HomePage } from "@features/home";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      {
        index: true,
        element: <HomePage />,
      },
    ],
  },
]);