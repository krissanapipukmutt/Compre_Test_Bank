import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { LanguageDisplayControl } from "./LanguageDisplayControl";

describe("language display control", () => {
  it("exposes compact accessible options and reports presentation changes", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    render(
      <LanguageDisplayControl mode="english_only" onChange={onChange} />,
    );

    const bilingual = screen.getByRole("button", {
      name: "English and Thai",
    });
    const english = screen.getByRole("button", { name: "English only" });
    expect(bilingual).toHaveTextContent("EN + TH");
    expect(english).toHaveTextContent("EN only");
    expect(english).toHaveAttribute("aria-pressed", "true");

    await user.click(bilingual);
    expect(onChange).toHaveBeenCalledWith("bilingual");
  });
});
