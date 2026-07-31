# Mock Examination Language-Switch Report

**Validated:** 2026-07-31
**Result:** PASS

## Tested learner workflow

1. Opened Mock Examination setup in bilingual mode.
2. Selected `English only` before starting.
3. Started a 10-question, 30-minute randomized mock session.
4. Confirmed the Thai stem was hidden and no answer/correctness feedback
   existed.
5. Selected a choice known from the test fixture to be incorrect.
6. Captured the session ID, question IDs/order, choice IDs/order, selected
   answer, submitted IDs, question index, timer start, and visible remaining
   time.
7. Switched to `English and Thai`.
8. Confirmed the same question ID, choice order, checked answer, question
   index, session ID, and timer origin.
9. Confirmed the timer decreased normally and did not restart.
10. Confirmed Thai question and choice content appeared while the answer panel
    and correctness classes stayed absent.
11. Switched repeatedly, moved to question 2, and confirmed the chosen mode
    persisted.
12. Moved to question 10, switched repeatedly immediately before final
    submission, and confirmed no early answer reveal.
13. Submitted the examination through the normal confirmation dialog.
14. Located the originally answered question in Results and confirmed the
    learner's incorrect selection, correct-answer styling, and bilingual
    explanation were available only after submission.
15. Switched Results to English-only and confirmed Thai question,
    choice/explanation, evidence-label, and source-path presentation was hidden
    while English feedback and score remained.
16. Switched Results back to bilingual and confirmed Thai feedback returned
    immediately.

## Refresh regression

A separate active-mock test selected an answer, moved to question 2, saved the
snapshot, and reloaded the route. The restored state matched the pre-refresh
snapshot:

- same session ID
- same question IDs and order
- same choice IDs and order
- same selected answer
- same submitted-answer set
- same current index
- same timer start and duration
- same global language preference

Returning to question 1 showed the original checked answer. Remaining time was
less than or equal to the pre-refresh value and was derived from the unchanged
absolute timer start. The stored session did not contain the rendered question
wording, demonstrating that the academic dataset was not duplicated.

## Mobile timed-exam regression

At 390×844:

- the sticky language toolbar remained visible above the exam-status toolbar;
- both language targets measured at least 44×44 CSS pixels;
- the language toolbar and timer/status toolbar did not overlap;
- selecting an answer and switching to bilingual retained the checked input;
- Thai appeared immediately;
- the timer continued to advance; and
- document-level horizontal overflow was at most one CSS pixel.

## State-safety verdict

Language switching did not:

- recreate the mock session;
- mutate the question or choice order;
- clear current or previous answers;
- submit an answer;
- alter the submitted-answer set;
- move the learner;
- restart, pause, or reset the timer;
- reveal correctness before final submission;
- change the result score;
- change bookmarks or the progress payload; or
- create language-specific answer copies.

The requested active-examination behavior is therefore complete.
