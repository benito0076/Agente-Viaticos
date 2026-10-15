import csv
import json
import os
import sys
import unicodedata
from datetime import date

from dotenv import load_dotenv
from google import genai

MODELO = "gemini-3.5-flash-lite"
CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_INSTRUCCIONES = os.path.join(CARPETA, "prompts", "sistema.md")
RUTA_CONOCIMIENTO = os.path.join(CARPETA, "conocimientos")
RUTA_GASTOS = os.path.join(RUTA_CONOCIMIENTO, "gastos.csv")
RUTA_SOLICITUDES = os.path.join(CARPETA, "solicitudes.csv")
MAX_VUELTAS = 5


def normalizar(texto):
    sin_tildes = unicodedata.normalize("NFD", texto)
    return "".join(c for c in sin_tildes if unicodedata.category(c) != "Mn").lower().strip()


def sumar_gastos(area=None, estado=None):
    with open(RUTA_GASTOS, encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))
    if area:
        filas = [f for f in filas if normalizar(f["area"]) == normalizar(area)]
    if estado:
        filas = [f for f in filas if normalizar(f["estado"]) == normalizar(estado)]
    return {"filas": len(filas), "total_cop": sum(int(f["valor_cop"]) for f in filas)}


def registrar_solicitud(empleado, ciudad, fecha_salida, noches, motivo):
    existe = os.path.exists(RUTA_SOLICITUDES)
    consecutivo = 1
    if existe:
        with open(RUTA_SOLICITUDES, encoding="utf-8", newline="") as archivo:
            consecutivo = sum(1 for _ in csv.DictReader(archivo)) + 1
    radicado = f"S-{consecutivo:03d}"
    with open(RUTA_SOLICITUDES, "a", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        if not existe:
            escritor.writerow(["radicado", "fecha", "empleado", "ciudad", "fecha_salida", "noches", "motivo", "estado"])
        escritor.writerow([radicado, date.today().isoformat(), empleado, ciudad, fecha_salida, noches,
                           motivo, "Pendiente de aprobación del jefe inmediato"])
    return {"radicado": radicado}


FUNCIONES = {"sumar_gastos": sumar_gastos, "registrar_solicitud": registrar_solicitud}
HERRAMIENTAS = [
    {
        "type": "function",
        "name": "sumar_gastos",
        "description": "Cuenta y suma en COP los gastos registrados en gastos.csv. Úsala siempre que se pida "
                       "sumar, contar o totalizar gastos. Ambos filtros son opcionales; sin filtros suma todo.",
        "parameters": {
            "type": "object",
            "properties": {
                "area": {"type": "string", "description": "Área de la empresa, por ejemplo Ventas."},
                "estado": {"type": "string", "description": "Estado del gasto, por ejemplo Aprobado o Pendiente."},
            },
        },
    },
    {
        "type": "function",
        "name": "registrar_solicitud",
        "description": "Registra una solicitud de viáticos y devuelve su radicado. Úsala solo cuando el usuario "
                       "pida registrar una solicitud y ya tengas los cinco datos.",
        "parameters": {
            "type": "object",
            "properties": {
                "empleado": {"type": "string", "description": "Nombre del empleado."},
                "ciudad": {"type": "string", "description": "Ciudad de destino."},
                "fecha_salida": {"type": "string", "description": "Fecha de salida, formato AAAA-MM-DD."},
                "noches": {"type": "integer", "description": "Número de noches del viaje."},
                "motivo": {"type": "string", "description": "Motivo del viaje."},
            },
            "required": ["empleado", "ciudad", "fecha_salida", "noches", "motivo"],
        },
    },
]

load_dotenv()
try:
    with open(RUTA_INSTRUCCIONES, encoding="utf-8") as archivo:
        INSTRUCCIONES = archivo.read().strip()
    documentos = []
    for nombre in sorted(os.listdir(RUTA_CONOCIMIENTO)):
        ruta = os.path.join(RUTA_CONOCIMIENTO, nombre)
        if os.path.isfile(ruta) and nombre.endswith(".md"):
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
entrada = " ".join(sys.argv[1:])
previa = None
for _ in range(MAX_VUELTAS):
    interaccion = client.interactions.create(
        model=MODELO,
        input=entrada,
        system_instruction=INSTRUCCIONES,
        tools=HERRAMIENTAS,
        previous_interaction_id=previa,
    )
    llamadas = [paso for paso in interaccion.steps if paso.type == "function_call"]
    if not llamadas:
        print(interaccion.output_text)
        break
    entrada = []
    for llamada in llamadas:
        try:
            resultado = FUNCIONES[llamada.name](**llamada.arguments)
        except Exception as error:
            resultado = {"error": str(error)}
        print(f"[HERRAMIENTA] {llamada.name}({llamada.arguments}) -> {resultado}")
        entrada.append({
            "type": "function_result",
            "name": llamada.name,
            "call_id": llamada.id,
            "result": [{"type": "text", "text": json.dumps(resultado, ensure_ascii=False)}],
        })
    previa = interaccion.id
else:
    sys.exit(f"El modelo no respondió con texto tras {MAX_VUELTAS} vueltas.")
