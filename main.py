import os
import json
import hashlib
from STT import STT
from flask import Flask, request, jsonify
from settings import Config

stt = STT(Config.model_dir)

app = Flask(__name__)
UPLOAD_FOLDER = Config.uploadfd
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_music():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    file_content = file.read()
    shaname = hashlib.sha256(file_content).hexdigest() + ".mp3"

    save_path = os.path.join(UPLOAD_FOLDER, shaname)
    with open(save_path, 'wb') as f:
        f.write(file_content)
        result = stt.to_text(f"{UPLOAD_FOLDER}/{shaname}")
    return jsonify({shaname: result})

if __name__ == '__main__':
    app.run(debug=Config.debug, host=Config.ip, port=Config.port)