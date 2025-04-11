from flask import Flask, request, jsonify, send_from_directory, send_file , render_template
import os
import requests
from dotenv import load_dotenv





from io import BytesIO


from docx import Document
from docx.shared import Inches, Pt
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.section import WD_ORIENT



load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}'


texto_global = ''

# @app.route('/', methods=['GET', 'POST'])
@app.route('/')
def index():
    # return send_from_directory('public', 'index.html')
    return render_template ('index.html')


@app.route('/consulta', methods=['POST'])
def consulta():
    global texto_global
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
        texto = resultado.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Sin respuesta.")
        texto = texto.replace('*','')
        texto_global = f'\n {texto} \n \n \n'

        return jsonify({"respuesta": texto})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/download-word')
def download_word():

    # Crear un documento de Word
    doc = Document()

    # Cambiar la orientación a horizontal
    # section = doc.sections[-1]
    # section.orientation = WD_ORIENT.LANDSCAPE

    # Ajustar el tamaño de la página al nuevo ancho
    # new_width, new_height = section.page_height, section.page_width
    # section.page_width = new_width
    # section.page_height = new_height
    global texto_global

    doc.add_heading('Informe de Optmización de CV con IA', 0)

    doc.add_paragraph(texto_global)







    # Guardar el documento en memoria
    output = BytesIO()
    doc.save(output)
    output.seek(0)

    # Enviar el archivo Word como respuesta
    return send_file(output, download_name="recomendacionesCV.docx", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
