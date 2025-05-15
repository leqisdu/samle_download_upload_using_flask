from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
import os
import hashlib
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = "your-secret-key"

UPLOAD_DIR = Path("uploaded")
if not UPLOAD_DIR.exists():
    UPLOAD_DIR.mkdir()

HASH_FILE = Path("file_hashes.json")
if not HASH_FILE.exists():
    with open(HASH_FILE, "w") as f:
        json.dump([], f)

def calculate_file_hash(file_obj, algorithm='sha256'):
    hash_func = hashlib.new(algorithm)
    file_obj.seek(0)
    while True:
        chunk = file_obj.read(8192)
        if not chunk:
            break
        hash_func.update(chunk)
    file_obj.seek(0)
    return hash_func.hexdigest()

def load_known_hashes():
    with open(HASH_FILE, 'r') as f:
        return json.load(f)

def save_known_hashes(hashes):
    with open(HASH_FILE, 'w') as f:
        json.dump(hashes, f, indent=2)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if not uploaded_file or uploaded_file.filename == "":
            flash("❌ No file selected.")
            return redirect(url_for("upload_file"))

        file_hash = calculate_file_hash(uploaded_file)
        known_hashes = load_known_hashes()

        if file_hash in known_hashes:
            flash("⚠️ File already uploaded.")
            return redirect(url_for("upload_file"))

        filename = uploaded_file.filename.replace(" ", "_")
        save_path = UPLOAD_DIR / filename
        uploaded_file.save(str(save_path))

        known_hashes.append(file_hash)
        save_known_hashes(known_hashes)

        flash(f"✅ Upload successful: {filename}")
        return redirect(url_for("upload_file"))

    files = [f.name for f in UPLOAD_DIR.iterdir() if f.is_file()]
    return render_template("upload.html", files=files)

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(str(UPLOAD_DIR), filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
