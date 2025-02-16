import os
import openai
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import spacy
import string
import json

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

        final=jsonify({"transcription": transcript.get("text", "")})
        return final
    except Exception as e:
        print("Transcription error:", e)
        return jsonify({"error": str(e)}), 500
    
final= json.loads(final.get_data(as_text=True))
final[0]['transcription']=Name_Age
final[1]['transcription']=Ed_Background
final[2]['transcription']=Grade
final[3]['transcription']=Subject
final[4]['transcription']=Understanding
final[5]['transcription']=Interests

def key_concepts(subject):
    words=f'extract the key concepts from;\n\n{subject}\n\nKey concepts:'
    response=openai.ChatCompletion.create(
        model='gpt-4-turbo',
        messages=[{'role':'system', 'content':'you are an AI chatbot who identifies key concepts.'},{'role':'user', 'content':words}]
    )
    concepts=response['choices'][0]['messages']['content']
    keywords=concepts.split(", ")
    return keywords


nlp = spacy.load("en_core_web_sm") # load pretrained model 

def proper_noun_extraction(x):
    prop_nouns = {}
    doc = nlp(string.capwords(x))
    proper_nouns=[]
    for tok in doc:
        if tok.pos_ == 'PROPN':
        prop_noun.append(str(tok))
    if proper_nouns:
        prop_nouns[x]=proper_nouns
        return prop_nouns
    else:
        return ('no proper noun found', None)

def provide_resources(keywords):
    prompt=f"""
    You are an AI academic assistant. Provide a list of high-quality academic resources on "{keywords}" including:
    
    1. **Books** (Author, Title, Summary)
    2. **Research Papers** (Title, Journal/Source, Summary, DOI/link if available)
    3. **Online Courses** (Course provider, Link, Brief Description)
    4. **Key Scholars** (Names, Contributions)
    
    Ensure resources are reputable, peer-reviewed, or from top universities. Format the response in markdown.
    """
    
    response=openai.ChatCompletion.create(
        model='gpt-4-turbo',
        messages=[{'role':'system', 'content':'you are an AI chatbot who identifies key concepts.'},{'role':'user', 'content':words}]
    )
    return response['choices'][0]['content']


understanding_levels={
    'one': 'a basic ability to understand the words and structure of the answer',
    'two':'an understanding of the vocabulary the prompt contains',
    'three':'an understanding of the subject matter',
    'four':'an ability to analyze the subject matter',
    'five':'an ability to ask follow-up questions about the subject matter',
    'six':'a mastery of the concept the prompt covers'
   
}

def user_progress:{
    'responses'=[],
    'scores'=[],
    'user_depth'=[]
}

def key_concepts(transcription):
    words=f'extract the key concepts from;\n\n{transcription}\n\nKey concepts:'
    response=openai.ChatCompletion.create(
        model='gpt-4-turbo',
        messages=[{'role':'system', 'content':'you are an AI chatbot who identifies key concepts.'},{'role':'user', 'content':words}]
    )
    concepts=response['choices'][0]['messages']['content']
    return concepts.split(", ")

def generate_question(concept, depth_level):
    depth_instruction = DEPTH_LEVELS.get(depth_level, "Ask a general question about this concept.")
    
    prompt = f"Generate a question that connects these concepts: '{concept}' based on this depth: {depth_instruction}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are an AI that asks questions at different levels of depth."},
        {"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

def answer_eval(user_answer, main_concept):
    prompt=f'''Evaluate the succinctness and clarity of the users answer, while also evaluating the accuracy of the answer in terms of the subject matter;
    concept:{main_concept}
    answer:{user_answer}
    Give a score based on Blooms Taxonomy (with a maximum level of 6) and explain your reasoning:
    Response Format:{{'score': X, 'reason':'...'}}'''
    
    feedback = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are an AI that responds to subject explanations with feedback and additional questions."},
        {"role": "user", "content": prompt}]
    import json
    try:
        feedback = json.loads(response["choices"][0]["message"]["content"])
        return feedback["score"], feedback["reason"]
    except:
        return 5, "Could not analyze response."
        
  
def question_adjustment(current_depth, score):
    avg=sum(previous_scores[-3:])/len(previous_scores) if previous_scores else scores
    if avg <= 4:
        return min(current_depth + 1, 6)
    if previous_scores[-1] = 4:
        return (current_depth)
    if avg => 4:
        return ('you have a firm grasp on this concept!')


def full():
   explanation = input("Enter your explanation: ")
    concepts = key_concepts(explanation)  # Extract concepts
    if not concepts:
        print("Could not extract concepts from prompt.")
        return

    main_concept = concepts[0]  # Use the first extracted concept
    depth_level = 3  # Start at medium difficulty

    while True:
        # Generate and ask a question
        question = generate_question(main_concept, depth_level)
        print(f"AI: {question}")

        # Get user response
        user_answer = input("Your answer: ")
        if user_answer.lower() in ["exit", "quit"]:
            print("Session ended.")
            break

        # Evaluate the answer
        score, reason = evaluate_answer(user_answer, main_concept)
        print(f"AI Feedback: {reason} (Score: {score}/10)")

        # Store user progress
        user_progress["responses"].append(user_answer)
        user_progress["scores"].append(score)
        user_progress["depth_levels"].append(depth_level)

        # Adjust depth level based on score history
        depth_level = adjust_depth(depth_level, score, user_progress["scores"])

        print(f"Next question will be at depth level: {depth_level}")

        # Show progress summary after every 3 questions
        if len(user_progress["scores"]) % 3 == 0:
            avg_score = sum(user_progress["scores"]) / len(user_progress["scores"])
            print(f"\n📊 Progress Report: Average Score = {avg_score:.2f}/10")
            print(f"🧐 Last 3 Scores: {user_progress['scores'][-3:]}")
            print(f"📈 Depth Level History: {user_progress['depth_levels']}\n")


if __name__ == "__main__":
    app.run(debug=True)
