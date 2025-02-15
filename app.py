import streamlit as st
import asyncio
import websockets
import speech_recognition as sr

st.title("Real-Time AI Voice Agent 🎙️")
st.write("Speak into the microphone and get real-time AI responses.")

recognizer = sr.Recognizer()

async def send_audio():
    async with websockets.connect("ws://localhost:8000/ws") as websocket:
        with sr.Microphone() as source:
            st.write("Listening...")
            while True:
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio)
                await websocket.send(text)
                response = await websocket.recv()
                st.text_area("AI Response:", response)

if st.button("Start Talking"):
    asyncio.run(send_audio())