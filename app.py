from flask import Flask, render_template, request, jsonify
from groq import Groq
import os
import base64
from dotenv import load_dotenv
# from pyngrok import ngrok  # Uncomment if you want to use ngrok

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Load API Keys
api_key = os.getenv("GROQ_API_KEY")
# ngrok_token = os.getenv("NGROK_TOKEN")  # Uncomment if using ngrok

# Ensure API key exists
if not api_key:
    raise ValueError("GROQ_API_KEY is missing in .env file")

# Initialize Groq client
client = Groq(api_key=api_key)

# Create uploads folder if not exists
os.makedirs("uploads", exist_ok=True)

def encode_image(image_path):
    """Convert image to base64 encoding"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    image = request.files['image']
    image_path = os.path.join("uploads", image.filename)
    image.save(image_path)
    
    base64_image = encode_image(image_path)

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is this image?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            model="llama-3.2-11b-vision-preview",
            temperature=0,
            max_tokens=1024,
            top_p=1,
            stream=False
        )

        response_text = chat_completion.choices[0].message.content
        os.remove(image_path)  # Clean up uploaded image
        return jsonify({"description": response_text})

    except Exception as e:
        os.remove(image_path)
        print(f"Error: {e}")  # Log the error
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # If you want to use ngrok, uncomment the following lines:
    # if not ngrok_token:
    #     raise ValueError("NGROK_TOKEN is missing in .env file")
    # public_url = ngrok.connect(5000)
    # print(f"Public URL: {public_url}")

    app.run(port=5000, debug=True)  # Debug mode enabled
