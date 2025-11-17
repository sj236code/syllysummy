# backend/app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from parser import extract_text_from_file, parse_syllabus

# -----------------------------------------------------------------------------
# Flask app setup
# -----------------------------------------------------------------------------
app = Flask(__name__)
CORS(app)

# Folder to temporarily store uploads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    """Simple health-check endpoint."""
    return jsonify({"status": "ok"}), 200


@app.route("/upload", methods=["POST"])
def upload_syllabus():
    """
    Accepts a syllabus file (PDF or .txt), extracts text,
    parses it, and returns structured JSON.
    """
    if "file" not in request.files:
        return jsonify({"error": "no file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "empty filename"}), 400

    filename = file.filename
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    try:
        text = extract_text_from_file(path)
        parsed = parse_syllabus(text)
    except Exception as e:
        # In a real app, log this
        return jsonify({"error": f"failed to parse syllabus: {e}"}), 500
    finally:
        # Best-effort cleanup
        try:
            os.remove(path)
        except Exception:
            pass

    return jsonify(parsed), 200


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # For local dev only
    app.run(debug=True)
