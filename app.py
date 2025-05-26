import os
import hashlib
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploaded'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def calculate_file_hash(file_storage):
    """Calculate the SHA256 hash of a file from FileStorage."""
    hash_sha256 = hashlib.sha256()
    file_storage.stream.seek(0)  # Ensure we're reading from the start
    for chunk in iter(lambda: file_storage.stream.read(4096), b""):
        hash_sha256.update(chunk)
    file_storage.stream.seek(0)  # Reset stream position after reading
    return hash_sha256.hexdigest()

@app.route('/', methods=['GET'])
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist('files[]')
    response = {'uploaded': [], 'duplicates': []}

    for file in uploaded_files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_hash = calculate_file_hash(file)

        if os.path.exists(file_path):
            with open(file_path, "rb") as existing_file:
                existing_file_hash = hashlib.sha256(existing_file.read()).hexdigest()
            if existing_file_hash == file_hash:
                response['duplicates'].append(filename)
                continue

        file.save(file_path)
        response['uploaded'].append(filename)

    return jsonify(response)
    
@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(files)
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

