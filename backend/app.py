# backend/app.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

from parser import extract_text_from_file, parse_syllabus_ai, parse_syllabus

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/upload", methods=["POST"])
def upload_syllabus():
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
        print(">>> Using AI parser (Gemini HTTP)")
        parsed = parse_syllabus_ai(text)
    except Exception as e:
        print("!!! AI parsing failed at top level, falling back:", e)
        parsed = parse_syllabus(text)
    finally:
        try:
            os.remove(path)
        except Exception:
            pass

    return jsonify(parsed), 200


if __name__ == "__main__":
    app.run(debug=True)
