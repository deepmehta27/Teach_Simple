from fastapi import FastAPI, WebSocket
import openai
import speech_recognition as sr
import pyttsx3

app=FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

ttsengine=pyttsx3.init()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    recognizer = sr.Recognizer()

    while True:
        try:
            data = await websocket.receive_text()  
            response = generate_response(data)  
            audio_response = text_to_speech(response)  
            await websocket.send_text(audio_response)  
        except Exception as e:
            await websocket.send_text(f"Error: {str(e)}")
            
            
def generate_response(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-4-o",
        messages=[{"role": "user", "content": user_input}]
    )
    return response['choices'][0]['message']['content']


def text_to_speech(text):
    tts_engine.say(text)
    tts_engine.runAndWait()
    return text