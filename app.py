from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
import os

# Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# OpenAI client (OPENAI_API_KEY env var eken automaticma gannawa)
client = OpenAI()

# ---------- Routes ----------

@app.route("/")
def home():
    # main chat page
    return render_template("index.html")


@app.route("/notes")
def notes_page():
    # saved notes / reminders page
    return render_template("index1.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Front-end eken wena chat request handle karana route eka"""
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Empty message"}), 400

    try:
        chat_completion = client.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-3.5-turbo"),
                        messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly study helper bot for a student in Japan. "
                        "First detect the main language of the user's message "
                        "(Sinhala, English, or Japanese). "
                        "Then follow these strict rules:\n"
                        "- If the user writes in Sinhala → reply ONLY in Sinhala. "
                        "Do NOT mix English sentences, except for short technical terms in parentheses if really necessary.\n"
                        "- If the user writes in English → reply ONLY in English. "
                        "Do NOT include any Sinhala or Japanese text unless the user explicitly asks for translation.\n"
                        "- If the user writes in Japanese → reply ONLY in simple Japanese. "
                        "Do NOT mix Sinhala or long English sentences.\n"
                        "If the user mixes languages in one message, choose the language that appears the most "
                        "and reply only in that language."
                    ),
                },

                {
                    "role": "user",
                    "content": message,
                },
            ],
            max_tokens=300,
            temperature=0.7,
        )

        reply_text = chat_completion.choices[0].message.content
        return jsonify({"reply": reply_text})

    except Exception as e:
        # Render logs walata error eka print wenna
        print(f"/api/chat error: {e}", flush=True)
        return jsonify({"error": "Server error", "details": str(e)}), 500


# ---------- Local run ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
