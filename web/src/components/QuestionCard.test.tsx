import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { academicData } from "../data";
import { presentQuestion } from "../engine";
import { QuestionCard } from "./QuestionCard";
import { MISSING_VISUAL_WARNING } from "../visual";
import type { PresentedQuestion } from "../domain";
import { MISSING_TRANSLATION_WARNING } from "../translation";

const scoreable = presentQuestion(
  academicData.questions.find(
    (question) =>
      question.answer_status === "verified_from_course_material" &&
      !question.requires_human_review &&
      !question.has_visual_content,
  )!,
  "test",
  false,
);
const review = presentQuestion(
  academicData.questions.find(
    (question) => question.answer_status === "unresolvable_question",
  )!,
  "test",
  false,
);
const probability = presentQuestion(
  academicData.questions.find(
    (question) => question.answer_status === "probabilistic_recommendation",
  )!,
  "test",
  false,
);
const external = presentQuestion(
  academicData.questions.find(
    (question) => question.answer_status === "verified_from_external_source",
  )!,
  "test",
  false,
);
const diagram = presentQuestion(
  academicData.questions.find(
    (question) => question.question_id === "question-comprehensive-021",
  )!,
  "diagram",
  false,
);
const table = presentQuestion(
  academicData.questions.find(
    (question) => question.question_id === "question-comprehensive-080",
  )!,
  "table",
  false,
);

function renderQuestion(question: PresentedQuestion) {
  return render(
    <QuestionCard
      bookmarked={false}
      onBookmark={vi.fn()}
      onChange={vi.fn()}
      question={question}
      reveal={false}
      selectedChoiceIds={[]}
    />,
  );
}

describe("QuestionCard", () => {
  it("renders every question and choice in English-then-Thai order", () => {
    renderQuestion(scoreable);
    const englishQuestion = screen.getByText(scoreable.original_question_en);
    const thaiQuestion = screen.getByText(scoreable.question_th);
    expect(
      englishQuestion.compareDocumentPosition(thaiQuestion) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();

    const firstChoice = scoreable.choices[0]!;
    const englishChoice = screen.getByText(firstChoice.original_text_en);
    const thaiChoice = screen.getByText(firstChoice.text_th);
    expect(
      englishChoice.compareDocumentPosition(thaiChoice) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });

  it("blocks a question and shows a bilingual warning when Thai is missing", () => {
    const broken: PresentedQuestion = { ...scoreable, question_th: "" };
    renderQuestion(broken);
    expect(screen.getByRole("alert")).toHaveTextContent(
      MISSING_TRANSLATION_WARNING,
    );
    expect(screen.getAllByRole("radio")[0]).toBeDisabled();
  });

  it("renders long bilingual text and technical terms without truncation", () => {
    const marketing = presentQuestion(
      academicData.questions.find(
        (question) => question.question_id === "question-comprehensive-052",
      )!,
      "marketing",
      false,
    );
    renderQuestion(marketing);
    expect(screen.getByText(marketing.original_question_en)).toBeVisible();
    expect(screen.getByText(marketing.question_th)).toBeVisible();
    expect(
      screen.getByText("การขยายสายผลิตภัณฑ์ (Line Extension)"),
    ).toBeVisible();
    expect(screen.getByText("คำแปลภาษาไทย").closest(".translation-block")).not
      .toHaveStyle({ textOverflow: "ellipsis" });
  });

  it("renders Thai and seals answers until submission", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    const { rerender } = render(
      <QuestionCard
        bookmarked={false}
        onBookmark={vi.fn()}
        onChange={onChange}
        question={scoreable}
        reveal={false}
        selectedChoiceIds={[]}
      />,
    );
    expect(screen.getByText(scoreable.question_th)).toBeInTheDocument();
    expect(screen.queryByText(scoreable.explanation_en)).not.toBeInTheDocument();
    expect(
      screen.queryByText(/Verified from course materials/),
    ).not.toBeInTheDocument();
    await user.click(screen.getAllByRole("radio")[0]!);
    expect(onChange).toHaveBeenCalledWith([scoreable.choices[0]!.choice_id]);

    rerender(
      <QuestionCard
        bookmarked={false}
        onBookmark={vi.fn()}
        onChange={onChange}
        question={scoreable}
        reveal
        selectedChoiceIds={[scoreable.correct_answer as string]}
      />,
    );
    expect(screen.getAllByText(scoreable.explanation_en).length).toBeGreaterThan(0);
    const explanationEnglish = screen.getAllByText(
      scoreable.explanation_en,
    )[0]!;
    const explanationThai = screen.getAllByText(scoreable.explanation_th)[0]!;
    expect(
      explanationEnglish.compareDocumentPosition(explanationThai) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
    expect(screen.getByText(/Correct · ถูกต้อง/)).toBeInTheDocument();
  });

  it("keeps unresolved status sealed until review", () => {
    const { rerender } = render(
      <QuestionCard
        bookmarked={false}
        onBookmark={vi.fn()}
        onChange={vi.fn()}
        question={review}
        reveal={false}
        selectedChoiceIds={[]}
      />,
    );
    expect(
      screen.queryByText(/Answer remains unresolved/),
    ).not.toBeInTheDocument();
    expect(review.correct_answer).toBeNull();
    expect(screen.queryByText(review.explanation_en)).not.toBeInTheDocument();

    rerender(
      <QuestionCard
        bookmarked={false}
        onBookmark={vi.fn()}
        onChange={vi.fn()}
        question={review}
        reveal
        selectedChoiceIds={[]}
      />,
    );
    expect(screen.getAllByText(/Answer remains unresolved/).length).toBeGreaterThan(0);
  });

  it("shows the exact probability warning and full distribution only after reveal", () => {
    const { rerender } = render(
      <QuestionCard
        bookmarked={false}
        onBookmark={vi.fn()}
        onChange={vi.fn()}
        question={probability}
        reveal={false}
        selectedChoiceIds={[]}
      />,
    );
    expect(
      screen.queryByText(probability.probability_warning_en!),
    ).not.toBeInTheDocument();

    rerender(
      <QuestionCard
        bookmarked={false}
        onBookmark={vi.fn()}
        onChange={vi.fn()}
        question={probability}
        reveal
        selectedChoiceIds={[probability.final_answer as string]}
      />,
    );
    expect(
      screen.getAllByText(probability.probability_warning_en!).length,
    ).toBeGreaterThan(0);
    expect(screen.getByText(/Recommended answer:/)).toBeInTheDocument();
    for (const item of probability.probability_distribution) {
      expect(
        screen.getAllByText(
          new RegExp(`${item.probability_percentage}%$`),
        ).length,
      ).toBeGreaterThan(0);
    }
  });

  it("shows a descriptive authoritative-source link only after reveal", () => {
    const { rerender } = render(
      <QuestionCard
        bookmarked={false}
        onBookmark={vi.fn()}
        onChange={vi.fn()}
        question={external}
        reveal={false}
        selectedChoiceIds={[]}
      />,
    );
    expect(
      screen.queryByText(/Verified from external sources/),
    ).not.toBeInTheDocument();

    rerender(
      <QuestionCard
        bookmarked={false}
        onBookmark={vi.fn()}
        onChange={vi.fn()}
        question={external}
        reveal
        selectedChoiceIds={[external.final_answer as string]}
      />,
    );
    expect(
      screen.getByText(/Verified from external sources/),
    ).toBeInTheDocument();
    expect(screen.getAllByRole("link").some((link) => Boolean(link.textContent?.trim()))).toBe(true);
  });

  it("renders no visual container for a text-only question", () => {
    renderQuestion(scoreable);
    expect(screen.queryByTestId("question-visual")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /View original question image/ }),
    ).not.toBeInTheDocument();
  });

  it("renders an original diagram and a relational table before choices", () => {
    const { rerender } = renderQuestion(diagram);
    expect(screen.getAllByTestId("question-visual")).toHaveLength(1);
    expect(
      screen.getByAltText(diagram.visual_assets[0]!.alt_en),
    ).toBeInTheDocument();
    const firstChoice = screen.getAllByRole("radio")[0]!;
    expect(
      screen.getByTestId("question-visual").compareDocumentPosition(firstChoice) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();

    rerender(
      <QuestionCard
        bookmarked={false}
        onBookmark={vi.fn()}
        onChange={vi.fn()}
        question={table}
        reveal={false}
        selectedChoiceIds={[]}
      />,
    );
    expect(screen.getByAltText(/UNION operator/)).toBeInTheDocument();
  });

  it("supports multiple inline images and a visual attached to a choice", () => {
    const mainAsset = diagram.visual_assets[0]!;
    const multipleImages: PresentedQuestion = {
      ...diagram,
      visual_assets: [
        mainAsset,
        {
          ...mainAsset,
          asset_id: `${mainAsset.asset_id}-second`,
        },
        diagram.visual_assets[1]!,
      ],
    };
    const { rerender } = renderQuestion(multipleImages);
    expect(screen.getAllByTestId("question-visual")).toHaveLength(2);

    const visualChoice: PresentedQuestion = {
      ...scoreable,
      choices: scoreable.choices.map((choice, index) =>
        index === 0
          ? {
              ...choice,
              visual_assets: [
                {
                  ...mainAsset,
                  asset_id: `${choice.choice_id}-visual`,
                  placement: "within_choice",
                },
              ],
            }
          : choice,
      ),
    };
    rerender(
      <QuestionCard
        bookmarked={false}
        onBookmark={vi.fn()}
        onChange={vi.fn()}
        question={visualChoice}
        reveal={false}
        selectedChoiceIds={[]}
      />,
    );
    expect(screen.getAllByTestId("question-visual")).toHaveLength(1);
  });

  it("shows the exact bilingual failure state and disables answering", () => {
    const broken: PresentedQuestion = {
      ...diagram,
      visual_assets: diagram.visual_assets.map((asset, index) =>
        index === 0
          ? { ...asset, public_path: "/exam-assets/missing/question-visual-01.jpg" }
          : asset,
      ),
    };
    renderQuestion(broken);
    fireEvent.error(screen.getByAltText(broken.visual_assets[0]!.alt_en));
    expect(screen.getByRole("alert")).toHaveTextContent(MISSING_VISUAL_WARNING);
    expect(screen.getAllByRole("radio")[0]).toBeDisabled();
  });

  it("opens the original source image, zooms, closes with Escape, and restores focus", async () => {
    const user = userEvent.setup();
    renderQuestion(diagram);
    const opener = screen.getByRole("button", {
      name: /View original question image/,
    });
    await user.click(opener);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("100%")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Zoom in" }));
    expect(screen.getByText("125%")).toBeInTheDocument();
    expect(
      screen.getByTestId("visual-viewport").querySelector("img"),
    ).toHaveStyle({ transform: "scale(1.25)" });
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    await waitFor(() => expect(opener).toHaveFocus());
  });
});
