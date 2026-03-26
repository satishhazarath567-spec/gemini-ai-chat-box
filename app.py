import os
from flask import Flask, render_template, request, Response, stream_with_context
import google.generativeai as genai
from PIL import Image
import io

app = Flask(__name__)

# --- Configure Gemini ---
# Set your actual API Key here
genai.configure(api_key="AIzaSyDpCNBBTGxpoQ2arL9kMWtZq3NgepyaTwk")

# STRICT SYSTEM INSTRUCTION: This acts as the education filter.
SYSTEM_PROMPT = """
You are a strict Education AI Assistant for students.
1. Respond politely to greetings (Hi, Hello, Hey, Good Morning).
2. Answer ONLY study, academic, school, exam, or career questions (e.g., math, science, history, programming, writing tips).
3. For ANY non-educational topic (movies, sports, off-topic chat, creative writing, advice), you MUST reply ONLY with the exact phrase: NOT_VALID_PROMPT.
4. If an image is provided, analyze it ONLY for educational content.
5. Provide detailed, helpful explanations for academic topics.
"""

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash', # Fastest model for the streaming feel
    system_instruction=SYSTEM_PROMPT
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.form.get('msg', '').strip()
    image_file = request.files.get('image')
    
    # Process both message and optional image
    content_list = []
    if user_msg:
        content_list.append(user_msg)
    
    if image_file:
        img = Image.open(image_file.stream)
        content_list.append(img)
    
    # If no content is provided, do nothing
    if not content_list:
        return Response("No content received", mimetype='text/plain')

    def generate():
        try:
            # stream=True enables the real-time response feel
            response = model.generate_content(content_list, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"Error: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=5000)