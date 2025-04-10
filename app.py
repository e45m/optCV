from flask import Flask, request, jsonify, send_from_directory
import os
import requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_folder='public')

API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}'

@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

@app.route('/consulta', methods=['POST'])
def consulta():
    data = request.json
    prompt = data.get('prompt', '')

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, json=payload)
        response.raise_for_status()
        resultado = response.json()
        texto = resultado.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Sin respuesta válida.")
        return jsonify({"respuesta": texto})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

