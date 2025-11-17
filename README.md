Syllabus Summaries — AI-Powered Course Intelligence

React + Flask + Google Gemini (2.5 Flash)
An end-to-end full-stack application that automatically extracts and structures key information from university syllabi.

Overview

Syllabus Summaries is an AI-enhanced tool that allows students to upload a syllabus (PDF or text) and instantly receive an organized breakdown of the course, including:

Important due dates

Grading breakdown and percentages

Required vs. optional textbooks

Key course policies

A tailored “How to get an A” strategy

A predicted weekly workload visualization

This project leverages Flask for backend processing, React + TailwindCSS + Recharts for the frontend, and Google Gemini 2.5 Flash for AI-powered document understanding.

How AI Is Used

The application integrates Google Gemini 2.5 Flash through the REST generateContent API. AI assists by:

Structured Syllabus Parsing

Gemini reads the entire syllabus and returns structured JSON following a strict schema:

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

Policy Extraction

Gemini automatically identifies:

Attendance rules

Late work policies

Academic integrity statements

Exam expectations

AI usage rules

Prerequisites and course expectations

Grade Strategy Generation

The model produces a tailored “How to get an A” strategy based on grading weights, deadlines, and expectations.

Hybrid Parsing Pipeline

The backend uses a dual-path parser:

AI parser (primary)

Heuristic parser (fallback if AI fails, produces invalid JSON, or times out)

This ensures reliability even for long or messy syllabi.

Tech Stack
Frontend

React (Vite)

TailwindCSS

Recharts for workload graphs

Backend

Python Flask

Flask-CORS

pdfplumber (PDF extraction)

dateutil (date parsing)

requests (AI HTTP calls)

AI

Google Gemini 2.5 Flash (REST API)

Explicit JSON-schema prompts

Auto-cleaning of malformed or wrapped JSON

Graceful fallback to heuristics

System Architecture
frontend/
  src/
    App.jsx
    components/
      UploadForm.jsx
      SummaryView.jsx
    index.css

backend/
  app.py
  parser.py
  uploads/


Data Flow

User uploads a PDF/TXT syllabus

React sends file to Flask /upload

Flask extracts text via pdfplumber

AI attempts structured parsing

If AI fails → heuristic parser runs

JSON returned to frontend

React displays structured results + charts

Features

AI-driven syllabus parsing

Heuristic fallback system

Automatic grading breakdown extraction

Deadline and date detection

Textbook identification

AI-generated study strategy

Policy extraction

PDF and TXT support

Weekly workload visualization

Running the Project
Backend Setup
cd backend
pip install -r requirements.txt


Set your Gemini API key in backend/.env:

GEMINI_API_KEY=your_api_key_here


Start the backend:

python app.py


Backend runs at:
http://127.0.0.1:5000

Frontend Setup
cd frontend
npm install
npm run dev


Frontend runs at:
http://localhost:5173

Example Output
{
  "grading_breakdown": [
    { "name": "Midterm 1", "percent": 28 },
    { "name": "Midterm 2", "percent": 36 },
    { "name": "Final Exam", "percent": 36 }
  ],
  "textbooks": [
    "Computer Systems: A Programmer’s Perspective, 3rd Edition"
  ],
  "policies": [
    "Class attendance is mandatory.",
    "Late assignments are not accepted.",
    "Academic integrity violations will be reported."
  ],
  "how_to_get_A": "Focus on Midterm 2 and Final (36% each). Start reviewing textbook chapters early..."
}

Why This Project Is Resume-Ready

This project showcases:

AI Integration

Practical experience integrating modern LLMs

Schema-driven JSON prompts

Post-processing of AI output

Robust error handling for malformed responses

Full-Stack Software Engineering

A complete Flask REST API

A modern React + Tailwind UI

File uploading, state management, and data visualization

Handling CORS, environment variables, and HTTP requests

Backend Strength

PDF parsing

Date parsing with natural language formats

Regex-based heuristics

Defensive programming and fallbacks

System Design Skills

Clean module organization

Scalable architecture

Stateful frontend + stateless backend pipeline

This project aligns well with expectations for SWE internship and new-grad candidates.

Future Enhancements

Export deadlines to Google Calendar

OCR for scanned PDFs

User accounts and saved syllabi

Cloud deployment (Vercel + Railway)

Offline syllabi classification

Progressive workload prediction