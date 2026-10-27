# STATUS — SSA Paperwork Calm Guide

As of 2026-10-27.

## What was built

A complete, education-only Social Security paperwork manual (never
benefits advice), in the house style of the sibling guides (plain
English, warm, step by step, kind verbs) — with the sibling's
*Medicare* rule inverted on purpose: **every number here is official**,
sourced to ssa.gov, and nothing dollar-shaped is invented.

- `docs/index.md` — Start Here: the whole guide in six sentences, who
  it's for, the numbers policy (official sources only, year-labeled
  volatile amounts, no invented dollars), a route table, the
  education-only promise, and the not-affiliated notice.
- `docs/01-one-picture.md` — SSA in one ASCII picture: one worker's
  record with retirement / disability / family doors on one side and
  survivors on the other; SSI across the street (need-based, not paid
  from Social Security taxes); the Medicare sign-up desk; the cast of
  characters (SSA, my Social Security, the 800-number, the field
  office, OIG, your binder); the official numbers table (2026 credit
  $1,890, four a year, 40 for retirement, highest-35-years amounts,
  credits never expire) with sources.
- `docs/02-which-appointment.md` — appointment types you may skip
  entirely, the three kinds of contact (no appointment / phone /
  in-person), the "your sentence → likely path" table, official
  scheduling rules (1-800-772-1213, 8 a.m.–7 p.m. weekdays), field
  offices 9–4 M–F via the locator, and the gentle "make the call that
  needs nothing" close.
- `docs/03-document-grab-list.md` — the originals protocol (original
  or certified; photocopies OK for W-2s/tax/medical; SSA returns what
  it sees), everyone's grab-list, per-claim add-ons (SSA-2 marriage
  certificate + decree; the Disability Starter Kit + SSA-3368/827; the
  survivors list from SSA-10), and SSA's own don't-delay rule.
- `docs/04-phone-field-online.md` — the three doors compared honestly;
  official quiet calling times (8–10 a.m. or later; midweek to Friday;
  later in the month); the kind phone script with the three things to
  write down; field-office visit steps; the online account step by
  step (ssa.gov/apply → my Social Security via Login.gov/ID.me →
  confirmation number → documents list → summary saved); direct-deposit
  patience note (30–60 days; don't close the old account).
- `docs/05-spouse-claims.md` — riding on a record explained slowly:
  "up to half," the family maximum (150%–180%), caretaker spouse at any
  age, the five divorced-spouse rules, Form SSA-2's online rule (within
  3 months of 62), the "no penalty for asking" protocol, and the
  Fairness Act update (WEP/GPO ended for benefits payable January 2024
  and later) — plus a pencil-sketch case with deliberately no dollars.
- `docs/06-survivor-claims.md` — the grief-paced chapter: report a
  death (funeral homes usually do; else call with name/SSN/DOB/DOD),
  the official percentage table (100% at survivor-FRA, 71–99% from 60,
  caretakers and children at 75%, disabled widow(er) from 50), the
  survivor-FRA table (66 for 1945–56 births, 67 for 1962+), the $255
  payment within 2 years, no online application, prompt applying
  (some claims pay from application date), the two already-receiving-
  benefits paths, remarriage rules, month-of-death payments, payment
  Wednesday bands, and representative payee/advance-designation notes.
- `docs/07-avoiding-scams.md` — SSA's official never-list verbatim,
  the two official "actually yes" facts (when SSA does call; opt-in
  texts only), the impersonator's toolkit table (frozen number,
  urgent arrest, fake badge, spoofed caller ID, COLA phish, lookalike
  sites, fee scams), a five-step first-aid list (oig.ssa.gov, FTC),
  and a printable scam-proofing checklist.
- `docs/08-claim-binder.md` — six tabs (Contacts; Identity & documents;
  Claim records; Money & deposits; Notes & worksheets; Scams & safety),
  the before/during/after ritual, privacy rules (SSN card stays home;
  no emailing certificates; shred), offline backup, and the ADHD-
  friendly 15-minutes-a-month low-energy mode.
- `docs/09-glossary.md` — ~45 plain-words definitions plus "words that
  sound scarier than they are."
- `docs/disclaimer.md` — the education-only promise, with the
  capitalized anti-advice clause and the who-answers-what table.
- `docs/worksheets/` — five printable worksheets: Appointment Finder,
  Document Grab-List Checklist, My Claim Timeline, Phone Call Notes,
  Binder Inventory.
- `build.py` (+ `build.sh`) — zero-dependency Python 3 stdlib static
  site builder: Markdown → HTML with sidebar nav, print-friendly CSS
  in `assets/style.css`, and a `--check` mode verifying every internal
  link and anchor (including `../`-relative targets).
- `tests/test_build.py` (+ `test.sh`) — 46 tests, described below.
- `README.md`, `LICENSE` (MIT), `.gitignore`.

Every doc carries the line "never medical, legal, financial, or
benefits advice"; the guide consistently points decisions to SSA
itself (1-800-772-1213, ssa.gov, field offices). It is not affiliated
with or endorsed by the Social Security Administration.

## How to run it

```bash
python3 build.py --check   # build site/ + verify all internal links
./test.sh                  # full test suite (also builds the site)
```

Then open `site/index.html` in a browser. Fully offline afterwards; no
network, accounts, or trackers. Python 3 standard library only.

## Verification results

- `python3 build.py --check` → builds all 17 files (16 pages + CSS);
  "Link check: all internal links resolve."
- `./test.sh` → **46 tests, all OK**:
  - build produces every chapter/worksheet/disclaimer page plus the
    stylesheet; every page has the 16-entry nav, the education-only
    sidebar notice, and the official 800-number; footer copyright and
    the not-affiliated notice are present; no `file://` URLs or
    absolute local paths in output;
  - internal links and anchors resolve (anchor checker now normalizes
    `../` targets — a fix made during this pass), and the checker
    provably flags a deliberately broken link;
  - converter regressions guarded (headings/IDs, paragraphs, lists
    incl. checkbox items and wrapped-item continuation, tables, fenced
    code escaping, blockquotes, inline bold/italic/nested emphasis,
    bold across wrapped lines, escaping, hr);
  - content guards: the one-picture diagram, year-labeled official
    credit amount with its FAQ trace, appointment paths and locator,
    all four document lists, the three doors, spouse-clause markers
    (up to half / 150%–180% / 10-year rule / Fairness Act), survivor
    markers (percentages, $255, 2 years, no online claim, payee),
    scam never-list, six binder tabs, glossary terms, the capitalized
    promise, every doc's education-only line, all five worksheets
    (printable + fill-in-the-blank), and chapters with numbers ending
    in sourced "Where these … come from" sections.
- **Numbers policy enforced by tests:** the only dollar figures that
  may appear are the sourced official ones ($1,890 — 2026 credit,
  year-labeled; $255 lump-sum death payment; the $442 million FTC
  figure SSA itself cites), and the official phone/TTY numbers must
  appear in their exact spelling wherever they appear.
- **Official-source verification considered done:** every number,
  phone number, window, and rule in the manual was checked against
  ssa.gov pages and publications during this pass — the credits FAQ
  (KA-02459), *How You Earn Credits* (05-10072), the retirement
  planner's documents page and FAQ KA-01891, *Timing your first
  payment*, Form SSA-1/SSA-2/SSA-10, *Survivors Benefits*
  (05-10084), *Understanding the Benefits* (05-10024), *What Every
  Woman Should Know* (05-10127), *What to do when someone dies*, the
  appointment FAQ (KA-02771), the imposter-fraud FAQ (KA-10018) and
  blog posts, the payment schedule (05-10031), the Medicare-only
  application page, *What You Need to Know When You Get Retirement or
  Survivors Benefits* (05-10077), the locator, and SSA's
  disability pages — each named in the chapter-end source lists.
- HTTP smoke test (local `http.server`): `/`, one chapter page, one
  worksheet, and `style.css` all return 200; rendered spot-checks show
  correct tables (7-cell call-log rows), one escaped ASCII-diagram
  `<pre>` per designed page, and the education-only line on all 17
  pages.
- Fixes made during this pass: `check_links` now normalizes `../`
  relative targets (the sibling anchoring bug surfaced by cross-file
  anchor links here); several draft typos reworded; the offline
  freshness test, converter tests, and hygiene tests extended to this
  guide's guardrails.

## Known gaps

- **Year-labeled numbers age.** The $1,890 credit amount is labeled
  2026 with its official page; ssa.gov re-sets the amount each year,
  so a future maintainer refreshes one number (and any new official
  amounts) rather than the whole chapter. Other pure dollar figures
  ($255, the FTC totals) are stable in the sources.
- **Disability is a path chapter, not a manual:** it covers applying
  (online/starter kit/by appointment), the five-month SSDI waiting
  period and its ALS exception, and SSI's first-month rule, but not
  the full adjudication/reconsideration journey — that deserves the
  same patient depth later, or a dedicated companion.
- No search function or dark mode on the built site; sidebar nav only
  (consistent with sibling guides).
- US-specific by nature; other regions would need their own guide.
- The site is static HTML; the worksheets print via the browser's
  print dialog (print CSS included), not generated PDFs.
- Companion-project links (medicare-decoded-guide,
  free-official-help-directory, bereavement-paperwork-guide) are by
  name, not URL, since they are sibling repositories with no fixed
  relationship in-repo.
- The spousal caretaker percentage is deliberately stated only in the
  survivor context (where the official publication states 75%);
  the living-worker caretaker amount is described by shape — SSA
  computes it during the claim.
