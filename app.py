from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__, static_folder="public", static_url_path="")

API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={API_KEY}"

@app.route("/")
def index():
    return send_from_directory("public", "index.html")

@app.route("/consulta", methods=["POST"])
def consulta():
    data = request.get_json()
    prompt = data.get("prompt", "")

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=body)
        response.raise_for_status()
        respuesta = response.json().get("candidates", [])[0]["content"]["parts"][0]["text"]
        return jsonify({"respuesta": respuesta})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
