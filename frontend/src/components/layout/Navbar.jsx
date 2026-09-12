import { NavLink } from "react-router-dom";
import { FiSettings } from "react-icons/fi";
import useAuth from "../../hooks/useAuth";
import BrandLogo from "./BrandLogo";
import ThemeToggle from "./ThemeToggle";
import Button from "../ui/Button";

const privateLinks = [
  { label: "Dashboard", to: "/dashboard" },
  { label: "Resume", to: "/resume" },
  { label: "Generate Interview", to: "/generate-interview" },
  { label: "History", to: "/history" },
];

function getInitials(name) {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/);
  const initials = parts.slice(0, 2).map((part) => part[0]?.toUpperCase());
  return initials.join("") || "?";
}

function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      <NavLink className="navbar__brand" to="/dashboard">
        <BrandLogo />
      </NavLink>

      <nav className="navbar__links" aria-label="Main navigation">
        {privateLinks.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              isActive ? "navbar__link navbar__link--active" : "navbar__link"
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="navbar__user">
        <span className="navbar__avatar">{getInitials(user?.username)}</span>
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            isActive ? "navbar__icon-link navbar__icon-link--active" : "navbar__icon-link"
          }
          aria-label="Settings"
          title="Settings"
        >
          <FiSettings size={18} />
        </NavLink>
        <ThemeToggle />
        <Button variant="ghost" size="sm" onClick={logout}>
          Log out
        </Button>
      </div>
    </header>
  );
}

export default Navbar;
