# Data Model

## Academic graph

```text
FileInventory 1 ← n SourceReference
Subject 1 → n Chapter 1 → n Topic
Chapter 1 → n GlossaryEntry
Question n → 1 Subject / Chapter; Question n ↔ n Topic
Question 1 → n Choice
ExamSet n ↔ n Question
```

Every relationship uses stable string IDs. `Question.correct_answer` contains a choice ID or `null`; it never stores a choice position.

## Runtime academic types

- `Subject`: identity, code/title, term, bilingual overview/objectives, chapters, sources, mapping confidence/warning.
- `Chapter`: bilingual summary/detail, study aids, formulas, topics, evidence and confidence.
- `Topic` / `GlossaryEntry`: bilingual definition, parent IDs, source-reference IDs.
- `Question`: original/translated text, choice objects, stable answer, answer status, confidence, bilingual explanations, evidence, difficulty, cognitive level, warnings.
- `SourceReference`: file ID/path and page/slide range.

Runtime validation rejects duplicate IDs, missing parents, invalid choice answers, verified answers without evidence, or review-required answers that expose correctness.

## Browser-local schema

Storage key: `compre-study:v1`

The storage repository is the only module that accesses `localStorage` directly.

```ts
type LocalState = {
  schemaVersion: 1;
  bookmarks: { chapterIds: string[]; questionIds: string[] };
  attempts: Attempt[];
  preferences: {
    languageView: "bilingual" | "english" | "thai";
    feedbackMode: "immediate" | "delayed";
    randomizeQuestions: boolean;
    randomizeChoices: boolean;
  };
};
```

An `Attempt` stores its own ID/timestamp/mode, question IDs, displayed choice order, learner answers keyed by question ID, submitted state, duration, and per-subject/topic results. Academic answers remain in bundled validated data, never copied as array positions.

## Migration and failure

- Missing storage creates defaults.
- Invalid JSON or unknown future schema is quarantined in memory and replaced with defaults after a visible warning.
- Reset clears only `compre-study:v1` after confirmation.
