from flask import Flask, request, jsonify, send_from_directory, send_file , render_template
import os
import requests
from dotenv import load_dotenv
import psycopg2





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

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)



@app.route('/vX3zqMnAyB7gRtCH9fLdNpJE0WkTuhQ2xVaPiLsoY4cbUGjKeTwZ', methods=['POST'])
def reset_visitas():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS visitas;")
            cur.execute("""
                CREATE TABLE visitas (
                    id SERIAL PRIMARY KEY,
                    contador INTEGER NOT NULL
                );
            """)
            cur.execute("INSERT INTO visitas (contador) VALUES (0);")
        conn.commit()
    return "Base de datos reiniciada."



def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS visitas (
                    id SERIAL PRIMARY KEY,
                    contador INTEGER NOT NULL
                );
            """)
            cur.execute("SELECT COUNT(*) FROM visitas;")
            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO visitas (contador) VALUES (0);")
        conn.commit()

def incrementar_visitas():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE visitas SET contador = contador + 1 RETURNING contador;")
            visitas = cur.fetchone()[0]
        conn.commit()
    return visitas



# @app.route('/', methods=['GET', 'POST'])
@app.route('/')
def index():
    # return send_from_directory('public', 'index.html')
    init_db()
    visitas = incrementar_visitas()

    return render_template ('index.html',visitas=visitas)



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

    doc.add_heading('Informe de Optimización de CV con IA', 0)

    doc.add_paragraph(texto_global)







    # Guardar el documento en memoria
    output = BytesIO()
    doc.save(output)
    output.seek(0)

    # Enviar el archivo Word como respuesta
    return send_file(output, download_name="recomendacionesCV.docx", as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
