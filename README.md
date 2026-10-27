# SSA Paperwork Calm Guide

A warm, plain-English Social Security paperwork manual — education and
admin help only: what SSA is in one picture, which appointment you
likely need (or can skip entirely), a document grab-list by claim type,
the phone / field-office / online paths compared, spouse and survivor
claims explained patiently, avoiding impersonation scams, and your own
claim binder, with printable worksheets and a glossary.

**Education and paperwork help only.** Nothing in this project is
medical, legal, or financial advice — and it is never *benefits* advice.
It explains paperwork; it never tells you when to claim, never picks a
benefit, and never asks for personal information (because it can't:
it's a folder of Markdown files). Every number in the manual is
official — sourced to ssa.gov pages and publications, named at the end
of each chapter; nothing dollar-shaped is invented.

## Why

Social Security paperwork tends to arrive during life's least patient
weeks — a birthday, an illness, a funeral. This manual translates the
whole season "like a friend would": plain English, step by step, never
condescending, with official numbers and kind verbs, so the paperwork
stays learnable while the calendar does whatever it's doing.

## Read it

- **On GitHub-style readers:** just open the files in
  [`docs/`](docs/index.md) — they're plain Markdown.
- **As a local website (recommended):**

  ```bash
  python3 build.py          # builds the static site into site/
  python3 build.py --check  # build + verify every internal link
  ```

  Then open `site/index.html` in a browser. Works fully offline; no
  network, no accounts, nothing leaves your machine.

## What's inside

| Part | What it covers |
| --- | --- |
| [Start Here](docs/index.md) | The whole guide in six sentences |
| Ch. 1 — Social Security in One Picture | One worker's record; the doors it opens; SSI across the street; the Medicare desk |
| Ch. 2 — Which Appointment You Likely Need | Online / phone / in-person, the "what do I need → what to do" table, scheduling, the relief of no appointment at all |
| Ch. 3 — The Document Grab-List | Everyone's papers, plus per-claim add-ons; originals protocol; the don't-delay rule |
| Ch. 4 — Phone, Field Office, or Online | The three doors compared; official quiet calling times; the kind phone script; the online account, step by step |
| Ch. 5 — Spouse Claims, Patiently | Riding on a record; "up to half"; the family maximum; divorced-spouse rules; the Fairness Act update |
| Ch. 6 — Survivor Claims, Patiently | Reporting a death; who benefits pay; the $255 payment; no online path; remarriage rules; payment Wednesday |
| Ch. 7 — Avoiding Impersonation Scams | SSA's official never-list; the impersonator's toolkit; first aid; a scam-proofing checklist |
| Ch. 8 — Your Claim Binder | Six tabs, the before/during/after ritual, privacy rules, a 15-minutes-a-month low-energy mode |
| Ch. 9 — Glossary | Plain words for Social Security paper |
| [The Education-Only Promise](docs/disclaimer.md) | What this guide is, and is not |
| Worksheets | [Appointment Finder](docs/worksheets/appointment-finder-worksheet.md), [Document Grab-List Checklist](docs/worksheets/document-grab-list-checklist.md), [My Claim Timeline](docs/worksheets/claim-timeline-worksheet.md), [Phone Call Notes](docs/worksheets/phone-call-notes-worksheet.md), [Binder Inventory](docs/worksheets/binder-inventory-worksheet.md) |

## Testing

```bash
python3 -m unittest discover -s tests -v
```

The test suite builds the site, checks every internal link and anchor,
verifies all chapters/worksheets render, guards converter regressions,
and enforces the guardrails: education-only language in every doc, the
official-numbers policy (official phone numbers, sourced year-labeled
amounts, no invented dollar figures), and repo hygiene (no secrets, no
personal-data-shaped strings, the exact LICENSE copyright, the LLC
credit, the not-affiliated notice). Run after any edit.

## Companion projects

- **medicare-decoded-guide** — the health-insurance half of the age-65
  season, translated the same way; Social Security runs the Medicare
  sign-up desk, and this guide hands you over there.
- **free-official-help-directory** — vetted official, always-free
  services (SSA included), for anything this guide only names.
- **bereavement-paperwork-guide** — the wider aftermath of a loss, the
  season this guide's survivor chapter lives inside.

## Project details

- **License:** MIT — see [LICENSE](LICENSE).
- **Copyright (c) 2026 Asdale Dynamics, LLC** of Indiana — plain-English
  AI education, books, and practical life-admin tools
  (dylanasdale.github.io, *The Massive AI Manual*).
- **Not affiliated with or endorsed by the Social Security
  Administration.** Official facts live at [www.ssa.gov](https://www.ssa.gov/)
  and 1-800-772-1213 (TTY 1-800-325-0778).
- **Local-first and private:** static HTML from your own Markdown; no
  services, no trackers, no secrets, no personal data anywhere in the
  repo.
