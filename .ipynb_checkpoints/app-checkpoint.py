from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message}
            ],
            max_tokens=100,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        return jsonify({'reply': reply})
    except Exception as e:
        print("OpenAI error:", e)
        return jsonify({'error': 'API request failed', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
