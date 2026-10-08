import os
import sys

from dotenv import load_dotenv
from google import genai

MODELO = "gemini-3.5-flash-lite"
INSTRUCCIONES = "Responde siempre como cavernicola y en máximo tres frases"

load_dotenv()
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
