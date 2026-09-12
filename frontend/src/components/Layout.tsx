import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/" className="brand">
          HireAI
        </Link>
        <nav className="nav-links">
          {user?.role === "recruiter" || user?.role === "admin" ? (
            <>
              <NavLink to="/jobs">Jobs</NavLink>
              <NavLink to="/applications">Pipeline</NavLink>
            </>
          ) : (
            <>
              <NavLink to="/jobs">Browse jobs</NavLink>
              <NavLink to="/applications">My applications</NavLink>
              <NavLink to="/resume">My resume</NavLink>
            </>
          )}
          {user ? (
            <>
              <span className="muted">{user.email}</span>
              <button className="secondary" onClick={logout}>
                Log out
              </button>
            </>
          ) : (
            <NavLink to="/login">Log in</NavLink>
          )}
        </nav>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
