"""Tests for the SSA Paperwork Calm Guide.

Run with:  python3 -m unittest discover -s tests -v

Covers: building the static site, the Markdown converter's documented
subset, presence of all chapters/worksheets, internal link integrity,
education-only guardrails, the official-numbers policy (no invented
dollar figures; year-labeled official amounts; sourced chapters), and
repo hygiene (no secrets/personal-data-looking strings, exact LICENSE
copyright, README LLC credit, the not-affiliated notice).
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import build as build_mod  # noqa: E402


class BuildSiteTests(unittest.TestCase):
    """Actually build the site, then check the outputs."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.written = build_mod.build()

    def test_build_succeeds_and_creates_all_pages(self):
        expected = {
            Path("site") / Path(f).with_suffix(".html") for f, _ in build_mod.CHAPTERS
        }
        written = {Path(p) for p in self.written}
        self.assertEqual(
            written & expected, expected, "missing generated pages"
        )

    def test_style_sheet_is_copied(self):
        self.assertTrue((build_mod.SITE / "style.css").exists())

    def test_pages_have_nav_disclaimer_and_phone(self):
        for f, label in build_mod.CHAPTERS:
            page = (build_mod.SITE / f).with_suffix(".html")
            text = page.read_text(encoding="utf-8")
            self.assertIn(label, text, f"nav missing entry for {f}")
            self.assertIn("Education and paperwork help only", text)
            self.assertIn("1-800-772-1213", text)

    def test_pages_carry_not_affiliated_notice(self):
        index_text = (build_mod.SITE / "index.html").read_text(encoding="utf-8")
        # the notice wraps across lines in the markdown source
        self.assertIn("Not affiliated with or endorsed by the Social Security Administration",
                      re.sub(r"\s+", " ", index_text))

    def test_no_absolute_paths_or_file_urls(self):
        for html_file in build_mod.SITE.rglob("*.html"):
            text = html_file.read_text(encoding="utf-8")
            self.assertNotIn("file://", text)
            self.assertNotIn(str(build_mod.ROOT), text)

    def test_footer_copyright_present(self):
        index = (build_mod.SITE / "index.html").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC", index)

    def test_built_site_is_uptodate(self):
        """The repo copy of site/ (if present) matches a fresh rebuild."""
        for src in (ROOT / "docs").rglob("*.md"):
            rel = src.relative_to(build_mod.DOCS).with_suffix(".html")
            freshest = build_mod.SITE / rel
            if not freshest.exists():
                continue
            self.assertGreaterEqual(
                freshest.stat().st_mtime, src.stat().st_mtime,
                f"site/ stale for {rel} — rerun build.py",
            )


class LinkIntegrityTests(unittest.TestCase):
    def test_internal_links_resolve(self):
        build_mod.build()
        broken = build_mod.check_links()
        self.assertEqual(broken, [], "broken internal links found")

    def test_link_check_actually_works(self):
        # sanity: the checker should flag a deliberately broken link
        target = build_mod.SITE / "index.html"
        original = target.read_text(encoding="utf-8")
        marker = 'href="01-one-picture.html"'
        self.assertIn(marker, original)
        try:
            target.write_text(original.replace(marker, 'href="no-such-file.html"'), encoding="utf-8")
            broken = build_mod.check_links()
            self.assertTrue(any("no-such-file.html" in b for b in broken))
        finally:
            target.write_text(original, encoding="utf-8")
            build_mod.build()


class ConverterTests(unittest.TestCase):
    def conv(self, md: str) -> str:
        return build_mod.convert_markdown(md)

    def test_headings_get_ids(self):
        html_out = self.conv("## Which Appointment You Likely Need, Calmly")
        self.assertIn('id="which-appointment-you-likely-need-calmly"', html_out)

    def test_paragraph(self):
        html_out = self.conv("Just a paragraph.")
        self.assertEqual(html_out, "<p>Just a paragraph.</p>")

    def test_lists(self):
        html_out = self.conv("- one\n- two\n1. first\n2. second")
        self.assertIn("<ul>\n<li>one</li>\n<li>two</li>\n</ul>", html_out)
        self.assertIn("<ol>\n<li>first</li>\n<li>second</li>\n</ol>", html_out)

    def test_wrapped_list_item_joins(self):
        html_out = self.conv("- hospital\n  care bucket\n- doctors bucket")
        self.assertNotIn("<p>care bucket</p>", html_out)
        self.assertIn("<li>hospital care bucket</li>", html_out)

    def test_checkbox_list(self):
        html_out = self.conv("- [ ] task one\n- [ ] task two")
        self.assertIn("<li>[ ] task one</li>", html_out)

    def test_table(self):
        html_out = self.conv("| A | B |\n| --- | --- |\n| 1 | 2 |")
        self.assertIn("<table>", html_out)
        self.assertIn("<th>A</th>", html_out)
        self.assertIn("<td>2</td>", html_out)

    def test_fenced_code_escapes_brackets(self):
        html_out = self.conv("```\n[ ] checkbox\n```\n")
        self.assertIn("[ ] checkbox", html_out)
        self.assertNotIn("<ble", html_out)

    def test_blockquote(self):
        html_out = self.conv("> Hello there.\n> This is a quote.")
        self.assertIn("<blockquote>", html_out)
        self.assertIn("This is a quote.", html_out)

    def test_inline_elements(self):
        html_out = self.conv("**bold** and *soft* and `code`")
        self.assertIn("<strong>bold</strong>", html_out)
        self.assertIn("<em>soft</em>", html_out)
        self.assertIn("<code>code</code>", html_out)

    def test_bold_and_nested_emphasis(self):
        html_out = self.conv("**bold *nested* text** stays")
        self.assertIn("<strong>bold <em>nested</em> text</strong>", html_out)

    def test_bold_across_wrapped_lines(self):
        html_out = self.conv("a **bold\nphrase** here")
        self.assertIn("<strong>bold<br />phrase</strong>", html_out)

    def test_html_is_escaped(self):
        html_out = self.conv("Angle <brackets> & ampersands")
        self.assertIn("&lt;brackets&gt;", html_out)
        self.assertIn("&amp;", html_out)

    def test_hr(self):
        self.assertIn("<hr />", self.conv("---"))


class ContentPresenceTests(unittest.TestCase):
    DOCS = ROOT / "docs"

    def doc(self, name: str) -> str:
        return (self.DOCS / name).read_text(encoding="utf-8")

    def test_all_chapters_exist(self):
        for f, _ in build_mod.CHAPTERS:
            self.assertTrue((self.DOCS / f).exists(), f"missing doc {f}")

    def test_one_picture_diagram_present(self):
        text = self.doc("01-one-picture.md")
        self.assertIn("ONE WORKER'S RECORD", text)
        self.assertIn("SURVIVORS BENEFITS", text)
        self.assertIn("SSI", text)

    def test_official_numbers_year_labeled(self):
        text = self.doc("01-one-picture.md")
        self.assertIn("$1,890", text)          # 2026 credit amount, verified from ssa.gov
        self.assertIn("2026", text)            # ... explicit year label
        self.assertIn("KA-02459", text)        # ... traced to the official FAQ

    def test_appointment_paths_covered(self):
        text = self.doc("02-which-appointment.md")
        for marker in [
            "1-800-772-1213",
            "locator",
            "cannot be applied for online",
            "appointment",
            "my Social Security",
        ]:
            self.assertIn(marker, text)

    def test_document_lists_covered(self):
        text = self.doc("03-document-grab-list.md")
        for marker in [
            "birth certificate",
            "marriage certificate",
            "proof of the worker's death",
            "W-2",
            "DD-214",
            "certified",
            "do not have all the documents",
        ]:
            self.assertIn(marker.lower(), text.lower())

    def test_three_paths_covered(self):
        text = self.doc("04-phone-field-online.md")
        for marker in [
            "1-800-325-0778",
            "8:00 a.m. to 7:00 p.m.",
            "8 a.m. and 10 a.m.",
            "Login.gov",
            "ID.me",
            "locator",
            "30 to 60 days",
        ]:
            self.assertIn(marker, text)

    def test_spouse_claims_covered(self):
        text = re.sub(r"\s+", " ", self.doc("05-spouse-claims.md"))
        for marker in [
            "up to half",
            "150% to 180%",
            "at least 10 years",
            "SSA-2",
            "Fairness Act",
            "January 2024",
        ]:
            self.assertIn(marker, text)

    def test_survivor_claims_covered(self):
        text = self.doc("06-survivor-claims.md")
        for marker in [
            "funeral home",
            "100%",
            "71% to 99%",
            "75%",
            "$255",
            "2 years",
            "cannot apply for survivors benefits online",
            "payee",
        ]:
            self.assertIn(marker.lower(), text.lower())

    def test_scam_guards(self):
        text = self.doc("07-avoiding-scams.md")
        for marker in [
            "suspend your Social Security number",
            "gift card",
            "oig.ssa.gov",
            "reportfraud.ftc.gov",
            "Pay.gov",
            "badge",
            "www.ssa.gov",
        ]:
            self.assertIn(marker, text)

    def test_binder_six_tabs(self):
        text = self.doc("08-claim-binder.md")
        for marker in ["Contacts", "Identity & documents", "Claim records",
                       "Money & deposits", "Notes & worksheets", "Scams & safety",
                       "low-energy"]:
            self.assertIn(marker, text)

    def test_glossary_defines_key_terms(self):
        text = self.doc("09-glossary.md")
        for marker in [
            "Credits (work credits)",
            "Full retirement age (FRA)",
            "Survivors benefits",
            "Representative payee",
            "Pay.gov",
            "Spoofing",
            "TTY (1-800-325-0778)",
        ]:
            self.assertIn(marker, text)

    def test_disclaimer_promise_present(self):
        text = self.doc("disclaimer.md")
        self.assertIn("THIS GUIDE EXPLAINS PAPERWORK AND GIVES NO ADVICE", text)

    def test_all_five_worksheets_exist(self):
        names = [f for f, _ in build_mod.CHAPTERS if f.startswith("worksheets/")]
        self.assertEqual(len(names), 5)

    def test_worksheets_are_fill_in_the_blank(self):
        for f, _ in build_mod.CHAPTERS:
            if not f.startswith("worksheets/"):
                continue
            text = self.doc(f)
            self.assertIn("Print", text, f"{f} should print")
            self.assertGreaterEqual(text.count("____"), 2, f"{f} lacks blanks")

    def test_every_doc_carries_numbers_policy_or_sources(self):
        """Chapters that state numbers must end with an official-source list."""
        for f in ("01-one-picture.md", "02-which-appointment.md",
                  "03-document-grab-list.md", "04-phone-field-online.md",
                  "05-spouse-claims.md", "06-survivor-claims.md",
                  "07-avoiding-scams.md", "08-claim-binder.md"):
            text = self.doc(f)
            self.assertIn("Where these", text, f"{f} missing a sources section")
            self.assertIn("ssa.gov", text, f"{f} sources must name ssa.gov")

    def test_no_invented_dollar_figures(self):
        """The numbers policy, enforced: the guide invents no amounts."""
        for f in self.DOCS.rglob("*.md"):
            text = f.read_text(encoding="utf-8").lower()
            self.assertNotIn("teaching number", text, f"stray invented-number style in {f.name}")
            self.assertNotIn("every number is invented", text, f"stray invented-number style in {f.name}")

    def test_numbers_are_official_or_shape_only(self):
        """Dollar figures must be the official, sourced ones only.

        $1,890 — the 2026 credit amount (credits FAQ / How You Earn Credits)
        $255 — the one-time lump-sum death payment (official FAQ)
        $442 — the FTC loss figure SSA itself cites (advocates page)
        """
        official = {"$1,890", "$255", "$442"}
        for f in self.DOCS.rglob("*.md"):
            text = f.read_text(encoding="utf-8")
            for match in re.findall(r"\$[\d,]{2,}", text):
                self.assertIn(match, official, f"unsourced dollar figure {match!r} in {f.name}")
            if "$1,890" in text:
                self.assertIn("2026", text, f"$1,890 in {f.name} needs its year label")

    def test_official_phone_numbers_everywhere(self):
        """The phone numbers must appear in their exact official spelling."""
        for f in self.DOCS.rglob("*.md"):
            text = f.read_text(encoding="utf-8")
            for m in re.findall(r"1-800-77[02]-12\d\d", text):
                self.assertEqual(m, "1-800-772-1213")
            for m in re.findall(r"1-800-32\d-077\d", text):
                self.assertEqual(m, "1-800-325-0778")

    def test_disclaimer_in_every_doc(self):
        needle = "never medical, legal, financial, or benefits advice"
        for f in self.DOCS.rglob("*.md"):
            text = re.sub(r"\s+", " ", f.read_text(encoding="utf-8"))
            self.assertIn(needle, text, f"education-only line missing in {f.name}")

    def test_not_affiliated_notice_in_index(self):
        text = re.sub(r"\s+", " ", self.doc("index.md"))
        self.assertIn("Not affiliated with or endorsed by the Social Security Administration", text)

    def test_no_personal_looking_data(self):
        pattern = re.compile(r"\b(\d{3}-\d{2}-\d{4})\b")  # SSN-shaped strings
        for f in self.DOCS.rglob("*.md"):
            self.assertIsNone(pattern.search(f.read_text()), f"SSN-like string in {f.name}")


class RepoHygieneTests(unittest.TestCase):
    def test_license_exact_copyright(self):
        text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Asdale Dynamics, LLC", text)

    def test_readme_credits_llc(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", text)

    def test_no_obvious_secrets(self):
        pattern = re.compile(
            r"(api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9]{16,}|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,})",
            re.IGNORECASE,
        )
        for f in ROOT.rglob("*"):
            if not f.is_file() or f.name.startswith(".git"):
                continue
            if f.suffix not in {".py", ".md", ".css", ".txt"}:
                continue
            self.assertIsNone(pattern.search(f.read_text(errors="ignore")), f"secret-like string in {f}")


if __name__ == "__main__":
    unittest.main()
