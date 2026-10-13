import os
import sys

from dotenv import load_dotenv
from google import genai

MODELO = "gemini-3.5-flash-lite"
CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_INSTRUCCIONES = os.path.join(CARPETA, "prompts", "sistema.md")
RUTA_CONOCIMIENTO = os.path.join(CARPETA, "conocimientos")

load_dotenv()
try:
    with open(RUTA_INSTRUCCIONES, encoding="utf-8") as archivo:
        INSTRUCCIONES = archivo.read().strip()
    documentos = []
    for nombre in sorted(os.listdir(RUTA_CONOCIMIENTO)):
        ruta = os.path.join(RUTA_CONOCIMIENTO, nombre)
        if os.path.isfile(ruta):
            with open(ruta, encoding="utf-8") as archivo:
                documentos.append(f'<documento nombre="{nombre}">\n{archivo.read().strip()}\n</documento>')
    INSTRUCCIONES += "\n\n" + "\n\n".join(documentos)
except OSError as error:
    sys.exit(f"No se pudo leer un archivo del agente: {error}")
llave = os.getenv("GEMINI_API_KEY")
if not llave:
    sys.exit("Falta GEMINI_API_KEY en el archivo .env")
if len(sys.argv) < 2:
    sys.exit('Uso: python agente.py "tu pregunta"')

client = genai.Client(api_key=llave)
interaccion = client.interactions.create(
    model=MODELO,
    input=" ".join(sys.argv[1:]),
    system_instruction=INSTRUCCIONES,
)
print(interaccion.output_text)
