from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import os

# Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# OpenAI client (OPENAI_API_KEY env var eken automaticma gannawa)
client = OpenAI()

# ---------- PWA helper routes (manifest & service worker) ----------

@app.route("/manifest.json")
def manifest():
    # static/manifest.json serve karanawa
    return send_from_directory("static", "manifest.json")

@app.route("/sw.js")
def service_worker():
    # static/sw.js serve karanawa
    return send_from_directory("static", "sw.js")

# ---------- Page routes ----------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/notes")
def notes_page():
    return render_template("index1.html")


# ---------- Chat API ----------

@app.route("/api/chat", methods=["POST"])
def chat():
    """Front-end eken wena chat request handle karana route eka"""
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Empty message"}), 400

    try:
        # System prompt: script balala language decide karanawa.
        system_prompt = (
            "You are a friendly study helper bot for a student in Japan.\n"
            "Detect the main language from the user's message.\n"
            "- If the message contains Sinhala letters (අ-෴), reply ONLY in Sinhala.\n"
            "- Else if it contains Japanese letters (ぁ-ヶ,一-龯), reply ONLY in simple Japanese.\n"
            "- Otherwise, reply ONLY in English.\n"
            "Do NOT mix languages in one answer unless the user clearly asks you to translate."
        )

        chat_completion = client.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            max_tokens=500,
            temperature=0.7,
        )

        reply_text = chat_completion.choices[0].message.content
        return jsonify({"reply": reply_text})

    except Exception as e:
        print(f"/api/chat error: {e}", flush=True)
        return jsonify({"error": "Server error", "details": str(e)}), 500


# ---------- Local run ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
