import os
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext

from dotenv import load_dotenv
from google import genai

MODELO = "gemini-3.5-flash-lite"
INSTRUCCIONES = "Responde siempre como cavernicola y en máximo tres frases"

FONDO = "#05070f"
PANEL = "#0b1020"
CIAN = "#00f0ff"
MAGENTA = "#ff2bd6"
VERDE = "#39ff88"
ROJO = "#ff4d6d"
TEXTO = "#cfe8ff"
FUENTE = ("Consolas", 11)

CARPETA = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
load_dotenv(os.path.join(CARPETA, ".env"))
llave = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=llave) if llave else None


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AGENTE VIÁTICOS // v1.0")
        self.geometry("620x520")
        self.minsize(420, 340)
        self.configure(bg=FONDO)

        tk.Label(
            self, text="◢ AGENTE VIÁTICOS ◣", bg=FONDO, fg=CIAN,
            font=("Consolas", 18, "bold"),
        ).pack(pady=(14, 0))
        self.estado = tk.Label(
            self, text="● SISTEMA EN LÍNEA", bg=FONDO, fg=VERDE, font=("Consolas", 9)
        )
        self.estado.pack(pady=(0, 8))

        marco = tk.Frame(self, bg=CIAN, padx=1, pady=1)
        marco.pack(fill=tk.BOTH, expand=True, padx=14)
        self.conversacion = scrolledtext.ScrolledText(
            marco, wrap=tk.WORD, state=tk.DISABLED, font=FUENTE, bg=PANEL, fg=TEXTO,
            insertbackground=CIAN, relief=tk.FLAT, borderwidth=0, padx=10, pady=8,
        )
        self.conversacion.pack(fill=tk.BOTH, expand=True)
        self.conversacion.tag_config("usuario", foreground=CIAN, font=("Consolas", 11, "bold"))
        self.conversacion.tag_config("agente", foreground=MAGENTA)
        self.conversacion.tag_config("error", foreground=ROJO)

        barra = tk.Frame(self, bg=FONDO)
        barra.pack(fill=tk.X, padx=14, pady=14)
        marco_entrada = tk.Frame(barra, bg=MAGENTA, padx=1, pady=1)
        marco_entrada.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entrada = tk.Entry(
            marco_entrada, font=FUENTE, bg=PANEL, fg=TEXTO, insertbackground=CIAN,
            relief=tk.FLAT,
        )
        self.entrada.pack(fill=tk.X, ipady=7, padx=1)
        self.entrada.bind("<Return>", lambda _: self.enviar())
        self.entrada.focus_set()

        self.boton = tk.Button(
            barra, text="ENVIAR ▶", command=self.enviar, width=12, font=("Consolas", 11, "bold"),
            bg=FONDO, fg=CIAN, activebackground=CIAN, activeforeground=FONDO,
            disabledforeground="#3a5560", relief=tk.FLAT, highlightthickness=1,
            highlightbackground=CIAN, cursor="hand2",
        )
        self.boton.pack(side=tk.LEFT, padx=(10, 0), ipady=4)

        if not client:
            self.escribir("ERROR: falta GEMINI_API_KEY en el archivo .env\n", "error")
            self.estado.config(text="● SISTEMA FUERA DE LÍNEA", fg=ROJO)
            self.boton.config(state=tk.DISABLED)

    def escribir(self, texto, etiqueta=None):
        self.conversacion.config(state=tk.NORMAL)
        self.conversacion.insert(tk.END, texto, etiqueta)
        self.conversacion.see(tk.END)
        self.conversacion.config(state=tk.DISABLED)

    def enviar(self):
        pregunta = self.entrada.get().strip()
        if not pregunta or self.boton["state"] == tk.DISABLED:
            return
        self.entrada.delete(0, tk.END)
        self.escribir(f"> {pregunta}\n", "usuario")
        self.boton.config(state=tk.DISABLED, text="PROCESANDO…")
        self.estado.config(text="● PROCESANDO", fg=MAGENTA)
        threading.Thread(target=self.consultar, args=(pregunta,), daemon=True).start()

    def consultar(self, pregunta):
        try:
            interaccion = client.interactions.create(
                model=MODELO,
                input=pregunta,
                system_instruction=INSTRUCCIONES,
            )
            self.after(0, self.mostrar, f"[AGENTE] {interaccion.output_text}\n\n", "agente")
        except Exception as error:
            self.after(0, self.mostrar, f"[ERROR] {error}\n\n", "error")

    def mostrar(self, texto, etiqueta):
        self.escribir(texto, etiqueta)
        self.boton.config(state=tk.NORMAL, text="ENVIAR ▶")
        self.estado.config(text="● SISTEMA EN LÍNEA", fg=VERDE)
        self.entrada.focus_set()


if __name__ == "__main__":
    Aplicacion().mainloop()
