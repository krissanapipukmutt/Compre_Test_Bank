import { useEffect, useRef, useState, type ReactNode } from "react";
import type { Route } from "../router";
import { primarySection, routeHref } from "../router";
import type { LanguageDisplayMode } from "../languageDisplay";
import { Icon } from "./Common";
import { LanguageDisplayControl } from "./LanguageDisplayControl";

const navigation: {
  section: string;
  label: string;
  shortLabel: string;
  route: Route;
  icon: Parameters<typeof Icon>[0]["name"];
}[] = [
  {
    section: "home",
    label: "Dashboard",
    shortLabel: "Home",
    route: { name: "home" },
    icon: "home",
  },
  {
    section: "library",
    label: "Study library",
    shortLabel: "Library",
    route: { name: "library" },
    icon: "library",
  },
  {
    section: "practice",
    label: "Practice",
    shortLabel: "Practice",
    route: { name: "practice" },
    icon: "practice",
  },
  {
    section: "mock",
    label: "Mock exam",
    shortLabel: "Mock",
    route: { name: "mock" },
    icon: "mock",
  },
  {
    section: "progress",
    label: "Progress",
    shortLabel: "Progress",
    route: { name: "progress" },
    icon: "progress",
  },
];

function NavItems({
  route,
  onNavigate,
  compact = false,
}: {
  route: Route;
  onNavigate?: () => void;
  compact?: boolean;
}) {
  const active = primarySection(route);
  return (
    <>
      {navigation.map((item) => (
        <a
          aria-current={active === item.section ? "page" : undefined}
          className={`nav-item ${active === item.section ? "is-active" : ""}`}
          href={routeHref(item.route)}
          key={item.section}
          onClick={onNavigate}
        >
          <Icon name={item.icon} />
          <span>{compact ? item.shortLabel : item.label}</span>
        </a>
      ))}
    </>
  );
}

export function AppShell({
  route,
  children,
  languageDisplayMode,
  onLanguageDisplayChange,
}: {
  route: Route;
  children: ReactNode;
  languageDisplayMode: LanguageDisplayMode;
  onLanguageDisplayChange: (mode: LanguageDisplayMode) => void;
}) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (drawerOpen) {
      closeRef.current?.focus();
    }
  }, [drawerOpen]);

  useEffect(() => {
    if (!drawerOpen) return;
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setDrawerOpen(false);
        triggerRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [drawerOpen]);

  const closeDrawer = () => {
    setDrawerOpen(false);
    triggerRef.current?.focus();
  };

  return (
    <div className="app-frame">
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <aside className="desktop-rail">
        <a className="brand" href="#/">
          <span className="brand__monogram">C</span>
          <span>
            <strong>COMPRE</strong>
            <small>study fieldbook</small>
          </span>
        </a>
        <nav aria-label="Primary navigation" className="rail-nav">
          <NavItems route={route} />
        </nav>
        <div className="rail-language">
          <span>Language</span>
          <LanguageDisplayControl
            className="language-display-control--rail"
            mode={languageDisplayMode}
            onChange={onLanguageDisplayChange}
          />
        </div>
        <a className="rail-about" href="#/about">
          About the data
        </a>
        <p className="rail-private">Local only · no account</p>
      </aside>

      <header className="mobile-header">
        <a className="brand brand--mobile" href="#/">
          <span className="brand__monogram">C</span>
          <span>
            <strong>COMPRE</strong>
            <small>study fieldbook</small>
          </span>
        </a>
        <button
          aria-expanded={drawerOpen}
          aria-haspopup="dialog"
          aria-label="Open navigation menu"
          className="icon-button"
          onClick={() => setDrawerOpen(true)}
          ref={triggerRef}
          type="button"
        >
          <Icon name="menu" />
        </button>
      </header>

      <div className="mobile-language-bar">
        <span>Language</span>
        <LanguageDisplayControl
          mode={languageDisplayMode}
          onChange={onLanguageDisplayChange}
        />
      </div>

      {drawerOpen ? (
        <div className="drawer-backdrop" onMouseDown={closeDrawer}>
          <aside
            aria-label="Navigation menu"
            aria-modal="true"
            className="nav-drawer"
            onMouseDown={(event) => event.stopPropagation()}
            role="dialog"
          >
            <div className="drawer-header">
              <div>
                <strong>Navigate</strong>
                <small lang="th">ไปยังส่วนต่าง ๆ</small>
              </div>
              <button
                aria-label="Close navigation menu"
                className="icon-button"
                onClick={closeDrawer}
                ref={closeRef}
                type="button"
              >
                <Icon name="close" />
              </button>
            </div>
            <nav className="drawer-nav">
              <NavItems onNavigate={closeDrawer} route={route} />
            </nav>
            <a className="drawer-about" href="#/about" onClick={closeDrawer}>
              About data & privacy
            </a>
          </aside>
        </div>
      ) : null}

      <main className="main-content" id="main-content" tabIndex={-1}>
        {children}
      </main>

      <nav aria-label="Mobile primary navigation" className="bottom-nav">
        <NavItems compact route={route} />
      </nav>
    </div>
  );
}
