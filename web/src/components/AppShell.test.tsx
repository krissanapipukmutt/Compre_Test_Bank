import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { AppShell } from "./AppShell";

describe("responsive application navigation", () => {
  it("opens and closes the labelled mobile navigation drawer", async () => {
    const user = userEvent.setup();
    render(
      <AppShell
        languageDisplayMode="bilingual"
        onLanguageDisplayChange={() => undefined}
        route={{ name: "home" }}
      >
        <h1>หน้าหลัก</h1>
      </AppShell>,
    );
    expect(screen.getByText("หน้าหลัก")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /open navigation menu/i }));
    expect(screen.getByRole("dialog", { name: /navigation menu/i })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /close navigation menu/i }));
    expect(
      screen.queryByRole("dialog", { name: /navigation menu/i }),
    ).not.toBeInTheDocument();
  });
});
