# Syllabus Summaries — AI-Powered Course Intelligence

React + Flask + Google Gemini (2.5 Flash)  
An end-to-end full-stack application that automatically extracts and structures key information from university syllabi.

---

## Overview

Syllabus Summaries is an AI-enhanced tool that allows students to upload a syllabus (PDF or text) and instantly receive an organized breakdown of the course, including:

- Important due dates  
- Grading breakdown and percentages  
- Required vs. optional textbooks  
- Key course policies  
- A tailored “How to get an A” strategy  
- A predicted weekly workload visualization  

This project leverages Flask for backend processing, React + TailwindCSS + Recharts for the frontend, and Google Gemini 2.5 Flash for AI-powered document understanding.

---

## How AI Is Used

The application integrates Google Gemini 2.5 Flash through the REST `generateContent` API. AI assists by:

### Structured Syllabus Parsing

Gemini reads the entire syllabus and returns structured JSON following a strict schema:

```json
{
  "course_title": null,
  "instructor_name": null,
  "emails": [],
  "grading_breakdown": [],
  "deadlines": [],
  "textbooks_required": [],
  "textbooks_optional": [],
  "policies": [],
  "how_to_get_A": ""
}
```

## Policy Extraction

Gemini automatically identifies:
- Attendance rules
- Late work policies
- Academic integrity statements
- Exam expectations
- AI usage rules
- Prerequisites and course expectations

## Grade Strategy Generation

The model produces a tailored “How to get an A” strategy based on grading weights, deadlines, and expectations.

## Tech Stack

### Frontend
- React (Vite)
- TailwindCSS
- Recharts for workload graphs

### Backend
- Python Flask
- Flask-CORS
- pdfplumber (PDF extraction)
- dateutil (date parsing)
- requests (AI HTTP calls)

### AI
- Google Gemini 2.5 Flash (REST API)
- Explicit JSON- schema prompts
- Auto-cleaning of malformed or wrapped JSON
- Graceful fallback heuristics

## Features
- AI-driven syllabus parsing
- Heuristic fallback system
- Automatic grading breakdown extraction
- Deadline and date detection
- Textbook identification
- AI-generated study strategy
- Policy extraction
- PDF and TXT support
- Weekly workload visualization
