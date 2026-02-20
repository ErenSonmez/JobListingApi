import { Outlet } from "react-router-dom";

export const Layout = () => {
  return (
    <div className="app-container">
      <header>
        <h2>Job Listing App</h2>
      </header>

      <main>
        <Outlet />
      </main>

      <footer>
      </footer>
    </div>
  );
};