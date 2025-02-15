import os
import json
import uuid
import threading
import requests
import websocket
from flask import Flask, request, jsonify, send_file
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Retrieve OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# In-memory storage for tasks
tasks = {}

def text_to_speech_bytes(text):
    """
    Convert text to speech using OpenAI's TTS API.
    Returns the audio content (bytes) if successful, or None if an error occurs.
    """
    TTS_URL = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "tts-1",
        "input": text,
        "voice": "alloy"
    }
    response = requests.post(TTS_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        print("TTS Error:", response.json())
        return None

def run_ws_for_topic(task_id, topic):
    """
    Opens a WebSocket connection to OpenAI's Realtime API,
    sends the topic as instructions, waits for the AI response, generates TTS audio,
    and stores the results in the tasks dict.
    """
    WS_URL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    WS_HEADERS = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }

    def on_message(ws, message):
        print(f"Received message for task {task_id}: {message}")  # Debug log
        data = json.loads(message)
        # Check if we received a text response from the API.
        if "response" in data and "text" in data["response"]:
            response_text = data["response"]["text"]
            print("AI Response:", response_text)

            # Generate TTS audio for the response.
            audio_bytes = text_to_speech_bytes(response_text)

            # Update the task with the result.
            tasks[task_id]["response"] = response_text
            tasks[task_id]["audio"] = audio_bytes
            tasks[task_id]["status"] = "done"
            print(f"Task {task_id} updated to done.")  # Debug log
            ws.close()  # Close the WebSocket once we have the response.

    def on_open(ws):
        print(f"WebSocket connected for task {task_id}")
        # Send a request event with the topic instructions.
        event = {
            "type": "response.create",
            "response": {
                "modalities": ["text"],
                "instructions": f"Teach me about {topic} in a simple way."
            }
        }
        ws.send(json.dumps(event))

    ws_app = websocket.WebSocketApp(
        WS_URL,
        header=[f"Authorization: Bearer {OPENAI_API_KEY}", "OpenAI-Beta: realtime=v1"],
        on_open=on_open,
        on_message=on_message
    )
    # Run the WebSocket connection. This call will block until the connection is closed.
    ws_app.run_forever()

@app.route('/teach', methods=['POST'])
def teach():
    """
    Receives a JSON POST with {"topic": "<your topic>"}.
    Starts a background thread to process the topic and returns a unique task_id.
    """
    data = request.get_json()
    if not data or "topic" not in data:
        return jsonify({"error": "No topic provided"}), 400

    topic = data["topic"]
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "response": None, "audio": None}

    print(f"Task {task_id} created for topic '{topic}'")  # Debug log

    # Start a background thread to handle the WebSocket connection
    thread = threading.Thread(target=run_ws_for_topic, args=(task_id, topic))
    thread.start()

    return jsonify({"task_id": task_id})

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    """
    Returns the AI's text response for the given task_id.
    If the task is still processing, returns a 202 status.
    """
    task = tasks.get(task_id)
    if not task:
        print(f"Invalid task ID: {task_id}")  # Debug log
        return jsonify({"error": "Invalid task ID"}), 404

    if task["status"] != "done":
        print(f"Task {task_id} is still processing.")  # Debug log
        return jsonify({"error": "Result not ready"}), 202

    print(f"Task {task_id} response: {task['response']}")  # Debug log
    return jsonify({"response": task["response"]})

@app.route('/audio/<task_id>', methods=['GET'])
def get_audio(task_id):
    """
    Serves the TTS-generated audio for the given task_id.
    If the task is still processing, returns a 202 status.
    """
    task = tasks.get(task_id)
    if not task:
        print(f"Invalid task ID: {task_id}")  # Debug log
        return jsonify({"error": "Invalid task ID"}), 404

    if task["status"] != "done" or not task["audio"]:
        print(f"Audio for task {task_id} not ready.")  # Debug log
        return jsonify({"error": "Audio not ready"}), 202

    audio_bytes = task["audio"]
    return send_file(
        BytesIO(audio_bytes),
        mimetype='audio/wav',
        as_attachment=False,
        download_name='response_audio.wav'
    )

if __name__ == '__main__':
    app.run(port=5000)
