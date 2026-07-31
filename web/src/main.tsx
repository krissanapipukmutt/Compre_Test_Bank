import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import {
  applyLanguageDisplayMode,
  loadLanguageDisplayMode,
} from "./languageDisplay";
import "./styles.css";

const root = document.getElementById("root");
if (!root) {
  throw new Error("Application root element is missing");
}

applyLanguageDisplayMode(loadLanguageDisplayMode());

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
