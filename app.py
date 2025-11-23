from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__, static_folder="static")
CORS(app)

@app.route("/manifest.json")
def manifest():
    return app.send_static_file("manifest.json")

@app.route("/sw.js")
def service_worker():
    return app.send_static_file("sw.js")

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/notes")
def notes_page():
    return render_template("index1.html")

# -------------------------
# CHAT API
# -------------------------
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            max_tokens=150,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        return jsonify({'reply': reply})
    except Exception as e:
        print("OpenAI Chat Error:", e)
        return jsonify({'error': 'Chat API request failed', 'details': str(e)}), 500


# -------------------------
# NEW: IMAGE GENERATE API
# -------------------------
@app.route('/api/image', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    try:
        img_response = openai.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024"
        )

        # base64 image string
        b64_img = img_response.data[0].b64_json

        return jsonify({
            "image": "data:image/png;base64," + b64_img
        })

    except Exception as e:
        print("Image API Error:", e)
        return jsonify({
            'error': 'Image generation failed',
            'details': str(e)
        }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
