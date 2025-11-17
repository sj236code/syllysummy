# backend/parser.py
import re
import os
import json
from datetime import datetime
from typing import List, Dict, Any

from dotenv import load_dotenv
load_dotenv()

import pdfplumber
from dateutil import parser as date_parser
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"  # AiStudio v1 REST
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent"


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
# Date / deadline extraction (heuristic)
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
# Grading breakdown extraction (heuristic)
# -----------------------------------------------------------------------------
def extract_grading_breakdown(text: str) -> List[Dict[str, Any]]:
    """
    Find grading breakdown lines like:
      - "Exam 1 – 20%"
      - "Homework: 15%"
      - "Participation (10%)"
    """
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

        if re.search(r"\b\d{1,3}\s*%", line):
            p = re.search(r"(\d{1,3})\s*%", line)
            percent = int(p.group(1)) if p else None

            name = re.sub(r"\d{1,3}\s*%", "", line)
            name = re.sub(r"[:\-]+", "", name).strip()

            if not name and percent is None:
                continue

            items.append(
                {
                    "name": name or "Component",
                    "percent": percent,
                    "line": line,
                }
            )

    if not items:
        for m in re.finditer(r"([A-Za-z0-9 \-]+?)\s*\((\d{1,3})\s*%\)", area):
            name = m.group(1).strip(" -:")
            percent = int(m.group(2))
            line = m.group(0)
            items.append({"name": name, "percent": percent, "line": line})

    return items


# -----------------------------------------------------------------------------
# Textbooks / readings extraction (heuristic)
# -----------------------------------------------------------------------------
def extract_textbooks(text: str) -> List[str]:
    """
    Grab a rough list of textbook / reading lines.
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

            ll = line.lower()
            if len(line) > 30 or " by " in ll or "edition" in ll:
                books.append(line)

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
    weeks: Dict[str, int] = {}

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
# Heuristic parser (no AI) – fallback
# -----------------------------------------------------------------------------
def parse_syllabus(text: str) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {}
    parsed["dates"] = find_dates(text)
    parsed["grading_breakdown"] = extract_grading_breakdown(text)
    parsed["textbooks"] = extract_textbooks(text)
    parsed["how_to_get_A"] = heuristic_how_to_get_an_A(parsed)
    parsed["weekly_workload"] = predicted_weekly_workload(parsed)
    parsed["policies"] = []  # heuristic doesn't extract policies
    return parsed


# -----------------------------------------------------------------------------
# Gemini AI parser via HTTP
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Gemini AI parser via HTTP
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# Gemini AI parser via HTTP
# -----------------------------------------------------------------------------
def parse_syllabus_ai(text: str) -> Dict[str, Any]:
    """
    Uses Google Gemini (HTTP API) to parse ANY syllabus format into structured JSON.
    Falls back to heuristic if key is missing or anything fails.
    """
    if not GEMINI_API_KEY:
        return parse_syllabus(text)

    prompt = """
You are a highly accurate syllabus parser.
Extract structured information from the following syllabus.

Return ONLY valid JSON.
No commentary. No markdown.

JSON schema to follow exactly:

{
  "course_title": "string or null",
  "instructor_name": "string or null",
  "emails": ["string"],
  "grading_breakdown": [
    {
      "name": "string",
      "percent": 0,
      "details": "string"
    }
  ],
  "deadlines": [
    {
      "label": "string",
      "date_iso": "YYYY-MM-DD or null",
      "raw_line": "string"
    }
  ],
  "textbooks_required": ["string"],
  "textbooks_optional": ["string"],
  "policies": ["string"],
  "how_to_get_A": "string"
}

Be precise. Infer dates when written as ranges.
Separate required vs optional textbooks.
"""

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt + "\n\nSYLLABUS:\n" + text
                    }
                ]
            }
        ]
    }

    try:
        resp = requests.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=body,
            timeout=30,
        )
        resp_data = resp.json()

        if resp.status_code != 200:
            print("Gemini API error:", resp.status_code, resp_data)
            return parse_syllabus(text)

        # Extract the model's text (which SHOULD be JSON, but might be wrapped)
        raw = resp_data["candidates"][0]["content"]["parts"][0].get("text", "")
        raw_str = (raw or "").strip()

        if not raw_str:
            print("Gemini returned empty text, falling back to heuristic.")
            return parse_syllabus(text)

        # First try direct JSON
        try:
            data = json.loads(raw_str)
        except json.JSONDecodeError:
            # Try to extract the JSON object inside ``` or other noise
            start = raw_str.find("{")
            end = raw_str.rfind("}")
            if start != -1 and end != -1 and start < end:
                candidate = raw_str[start:end + 1]
                try:
                    data = json.loads(candidate)
                except json.JSONDecodeError as e2:
                    print("Failed to parse cleaned JSON candidate:", e2)
                    return parse_syllabus(text)
            else:
                print("Could not locate JSON braces in Gemini output.")
                return parse_syllabus(text)

    except Exception as e:
        print("Gemini HTTP call failed, using heuristic:", e)
        return parse_syllabus(text)

    # At this point we have a valid 'data' dict from Gemini
    parsed: Dict[str, Any] = {}

    parsed["grading_breakdown"] = [
        {
            "name": g.get("name"),
            "percent": g.get("percent"),
            "line": g.get("details") or "",
        }
        for g in data.get("grading_breakdown", [])
    ]

    parsed["dates"] = [
        {
            "raw": d.get("label"),
            "line": d.get("raw_line"),
            "parsed": d.get("date_iso"),
        }
        for d in data.get("deadlines", [])
    ]

    parsed["textbooks"] = (
        data.get("textbooks_required", []) +
        data.get("textbooks_optional", [])
    )

    how_to = data.get("how_to_get_A")
    if isinstance(how_to, str):
        parsed["how_to_get_A"] = how_to.strip()
    else:
        # fall back to heuristic if AI didn't give a string
        parsed["how_to_get_A"] = heuristic_how_to_get_an_A(parsed)

    parsed["policies"] = data.get("policies", [])
    parsed["weekly_workload"] = predicted_weekly_workload(parsed)

    return parsed
