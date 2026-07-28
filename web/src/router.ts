import { useEffect, useState } from "react";

export type Route =
  | { name: "home" }
  | { name: "library" }
  | { name: "subject"; code: string }
  | { name: "chapter"; chapterId: string }
  | { name: "topic"; topicId: string }
  | { name: "practice" }
  | { name: "practice-session" }
  | { name: "practice-review" }
  | { name: "mock" }
  | { name: "mock-exam" }
  | { name: "mock-results" }
  | { name: "progress" }
  | { name: "about" };

export function parseRoute(hash = window.location.hash): Route {
  const path = hash.replace(/^#\/?/, "").split("?")[0] ?? "";
  const parts = path.split("/").filter(Boolean);
  if (parts[0] === "library" && parts[1] === "subject" && parts[2]) {
    return { name: "subject", code: decodeURIComponent(parts[2]) };
  }
  if (parts[0] === "library" && parts[1] === "chapter" && parts[2]) {
    return { name: "chapter", chapterId: decodeURIComponent(parts[2]) };
  }
  if (parts[0] === "library" && parts[1] === "topic" && parts[2]) {
    return { name: "topic", topicId: decodeURIComponent(parts[2]) };
  }
  const simple: Record<string, Route> = {
    library: { name: "library" },
    practice: { name: "practice" },
    "practice-session": { name: "practice-session" },
    "practice-review": { name: "practice-review" },
    mock: { name: "mock" },
    "mock-exam": { name: "mock-exam" },
    "mock-results": { name: "mock-results" },
    progress: { name: "progress" },
    about: { name: "about" },
  };
  return simple[parts[0] ?? ""] ?? { name: "home" };
}

export function routeHref(route: Route): string {
  switch (route.name) {
    case "home":
      return "#/";
    case "subject":
      return `#/library/subject/${encodeURIComponent(route.code)}`;
    case "chapter":
      return `#/library/chapter/${encodeURIComponent(route.chapterId)}`;
    case "topic":
      return `#/library/topic/${encodeURIComponent(route.topicId)}`;
    default:
      return `#/${route.name}`;
  }
}

export function navigate(route: Route): void {
  const href = routeHref(route);
  if (window.location.hash === href) {
    window.dispatchEvent(new HashChangeEvent("hashchange"));
  } else {
    window.location.hash = href;
  }
  window.scrollTo({ top: 0, behavior: "instant" });
}

export function useRoute(): Route {
  const [route, setRoute] = useState<Route>(() => parseRoute());
  useEffect(() => {
    const update = () => setRoute(parseRoute());
    window.addEventListener("hashchange", update);
    return () => window.removeEventListener("hashchange", update);
  }, []);
  return route;
}

export function primarySection(route: Route): string {
  if (["subject", "chapter", "topic"].includes(route.name)) {
    return "library";
  }
  if (route.name.startsWith("practice")) {
    return "practice";
  }
  if (route.name.startsWith("mock")) {
    return "mock";
  }
  return route.name;
}
