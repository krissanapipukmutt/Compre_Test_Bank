# Information Architecture

```text
Application
├── Dashboard
│   ├── Continue studying
│   ├── Progress snapshot
│   └── Academic warnings
├── Library
│   ├── Term 1
│   │   ├── BIS602
│   │   ├── BIS605
│   │   └── BIS606
│   └── Term 2
│       ├── BIS601
│       ├── BIS603
│       └── BIS604
│           └── Subject → Chapter → Topic / Glossary / Sources
├── Practice
│   ├── Setup
│   ├── Session
│   └── Review
├── Mock exam
│   ├── Setup
│   ├── Active exam
│   └── Results / Review
├── Progress
│   ├── Overview
│   ├── Attempts
│   ├── Weak topics
│   └── Bookmarks
└── About data
    ├── Evidence/status definitions
    ├── Coverage and limitations
    └── Local privacy
```

## Routes

- `/` dashboard
- `/library`, `/library/:courseCode`, `/library/:courseCode/:chapterId`
- `/practice`, `/practice/session`, `/practice/review`
- `/mock`, `/mock/exam`, `/mock/results`
- `/progress`
- `/about`

The first version may implement routes through a lightweight history router to keep dependencies minimal. Reload and direct-link fallback are documented for static hosting.

## Navigation

- Desktop/tablet landscape: persistent left rail plus compact top utility bar.
- Phone/tablet portrait: top app bar and bottom primary navigation; secondary destinations live in a drawer.
- Breadcrumbs appear on subject/chapter pages and collapse to a back link on narrow phones.

