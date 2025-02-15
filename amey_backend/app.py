import os
import openai
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set your OpenAI API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise Exception("Please set your OPENAI_API_KEY environment variable.")

@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    if "file" not in request.files:
        return jsonify({"error": "No file provided."}), 400

    audio_file = request.files["file"]
    if audio_file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    try:
        # Create a temporary file with delete=False
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
            audio_file.save(tmp_path)
        
        # Open the temporary file for reading in binary mode
        # with open(tmp_path, "rb") as f:
        #     # Use the new interface for transcription
        #     transcript = openai.Audio.transcriptions.create(
        #         model="whisper-1",
        #         file=f,
        #         response_format="text"
        #     )

        with open(tmp_path, "rb") as f:
            transcript = openai.Audio.transcribe("whisper-1", f)
        
        # Remove the temporary file
        os.remove(tmp_path)

        return jsonify({"transcription": transcript.get("text", "")})
    except Exception as e:
        print("Transcription error:", e)
        return jsonify({"error": str(e)}), 500
    

    

if __name__ == "__main__":
    app.run(debug=True)
