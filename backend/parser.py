# backend/parser.py
import re
from datetime import datetime
from typing import List, Dict, Any

import pdfplumber
from dateutil import parser as date_parser


# -----------------------------------------------------------------------------
# Text extraction
# -----------------------------------------------------------------------------
def extract_text_from_file(path: str) -> str:
    """
    Extract raw text from a syllabus file.

    - If it's a PDF: use pdfplumber to get text per page.
    - If it's .txt (or anything else): open as plain text.
    """
    lower = path.lower()
    if lower.endswith(".pdf"):
        text_chunks = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_chunks.append(page_text)
        return "\n".join(text_chunks)

    # Fallback: treat as text file
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


# -----------------------------------------------------------------------------
# Date / deadline extraction
# -----------------------------------------------------------------------------
def find_dates(text: str) -> List[Dict[str, Any]]:
    """
    Very simple heuristic date finder.

    Returns a list of:
      { "raw": "...", "line": "...", "parsed": "YYYY-MM-DD" or None }
    """
    lines = text.splitlines()

    # Pattern: "Jan 15", "January 15, 2025", "9/15/24", "09/15"
    date_pattern = re.compile(
        r"""(
            (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s*\d{2,4})?
            |
            \d{1,2}/\d{1,2}(?:/\d{2,4})?
        )""",
        re.IGNORECASE | re.VERBOSE,
    )

    results: List[Dict[str, Any]] = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        for m in date_pattern.finditer(stripped):
            raw = m.group(1)
            parsed_iso = None
            try:
                dt = date_parser.parse(raw, fuzzy=True, dayfirst=False)
                parsed_iso = dt.date().isoformat()
            except Exception:
                pass

            results.append(
                {
                    "raw": raw,
                    "line": stripped,
                    "parsed": parsed_iso,
                }
            )

    return results


# -----------------------------------------------------------------------------
# Grading breakdown extraction
# -----------------------------------------------------------------------------
def extract_grading_breakdown(text: str) -> List[Dict[str, Any]]:
    """
    Find grading breakdown lines like:
      - "Exam 1 – 20%"
      - "Homework: 15%"
      - "Participation (10%)"
    """
    # Try to zoom into a region around "grading" or similar
    m = re.search(
        r"(grading|grade breakdown|evaluation|assessment|course grade)[\s\S]{0,1200}",
        text,
        flags=re.IGNORECASE,
    )
    area = m.group(0) if m else text

    items: List[Dict[str, Any]] = []

    for line in area.splitlines():
        line = line.strip()
        if not line:
            continue

        # Look for percentages
        if re.search(r"\b\d{1,3}\s*%", line):
            p = re.search(r"(\d{1,3})\s*%", line)
            percent = int(p.group(1)) if p else None

            # Remove the percent portion and cleanup
            name = re.sub(r"\d{1,3}\s*%", "", line)
            name = re.sub(r"[:\-]+", "", name).strip()

            # Ignore obviously weird lines
            if not name and percent is None:
                continue

            items.append(
                {
                    "name": name or "Component",
                    "percent": percent,
                    "line": line,
                }
            )

    # Fallback: look for "Thing (20%)"
    if not items:
        for m in re.finditer(r"([A-Za-z0-9 \-]+?)\s*\((\d{1,3})\s*%\)", area):
            name = m.group(1).strip(" -:")
            percent = int(m.group(2))
            line = m.group(0)
            items.append({"name": name, "percent": percent, "line": line})

    return items


# -----------------------------------------------------------------------------
# Textbooks / readings extraction
# -----------------------------------------------------------------------------
def extract_textbooks(text: str) -> List[str]:
    """
    Grab a rough list of textbook / reading lines.

    For the MVP we just return a flat list of lines that look like books;
    later we can split into required vs optional sections.
    """
    m = re.search(
        r"(required texts?|textbooks?|required reading|books?)[\s\S]{0,500}",
        text,
        flags=re.IGNORECASE,
    )
    area = m.group(0) if m else ""

    books: List[str] = []

    if area:
        for line in area.splitlines():
            line = line.strip()
            if not line:
                continue

            # crude heuristic: long-ish lines or lines mentioning "by" or "edition"
            ll = line.lower()
            if len(line) > 30 or " by " in ll or "edition" in ll:
                books.append(line)

    # de-duplicate while preserving order
    seen = set()
    unique_books = []
    for b in books:
        if b not in seen:
            seen.add(b)
            unique_books.append(b)

    return unique_books


# -----------------------------------------------------------------------------
# "How to get an A" heuristic
# -----------------------------------------------------------------------------
def heuristic_how_to_get_an_A(parsed: Dict[str, Any]) -> str:
    """
    Uses the grading breakdown + presence of textbooks to give basic advice.
    Can be replaced with an LLM later.
    """
    tips = []

    grades = parsed.get("grading_breakdown", [])
    if grades:
        with_weights = [g for g in grades if g.get("percent") is not None]
        if with_weights:
            sorted_by_weight = sorted(
                with_weights, key=lambda x: -x["percent"]
            )
            top = sorted_by_weight[0]
            tips.append(
                f'Focus on "{top["name"]}" — it counts for {top["percent"]}% of your grade.'
            )

    if parsed.get("textbooks"):
        tips.append(
            "Get access to the required textbook or course readings early, "
            "and skim chapters connected to big assignments or exams."
        )

    tips.append(
        "Show up consistently, keep track of all deadlines, and turn in every small assignment. "
        "Participation and low-stakes work often add up."
    )

    tips.append(
        "During the first two weeks, read any rubrics or grading policies carefully — "
        "they usually tell you exactly what 'A' work looks like."
    )

    return " ".join(tips)


# -----------------------------------------------------------------------------
# Weekly workload estimation
# -----------------------------------------------------------------------------
def predicted_weekly_workload(parsed: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Very rough: count how many deadlines fall in each calendar week.

    Returns:
      [{ "week": "2025-W02", "count": 3 }, ...]
    """
    weeks = {}

    for d in parsed.get("dates", []):
        iso = d.get("parsed")
        if not iso:
            continue

        try:
            dt = datetime.strptime(iso, "%Y-%m-%d")
        except Exception:
            continue

        year, week, _ = dt.isocalendar()
        key = f"{year}-W{week:02d}"
        weeks[key] = weeks.get(key, 0) + 1

    out = [{"week": k, "count": v} for k, v in sorted(weeks.items())]
    return out


# -----------------------------------------------------------------------------
# Top-level parser
# -----------------------------------------------------------------------------
def parse_syllabus(text: str) -> Dict[str, Any]:
    """
    Main function: given raw syllabus text, return the structured object
    that the frontend will consume.
    """
    parsed: Dict[str, Any] = {}

    parsed["dates"] = find_dates(text)
    parsed["grading_breakdown"] = extract_grading_breakdown(text)
    parsed["textbooks"] = extract_textbooks(text)
    parsed["how_to_get_A"] = heuristic_how_to_get_an_A(parsed)
    parsed["weekly_workload"] = predicted_weekly_workload(parsed)

    return parsed
