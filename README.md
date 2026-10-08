# Agente Viáticos

Agente de línea de comandos en Python que envía una pregunta a Gemini (`google-genai`) y muestra la respuesta. Por ahora responde como cavernícola en máximo tres frases; es la base para un agente de viáticos.

## Requisitos

- Python 3.10 o superior
- Una llave de API de Gemini ([Google AI Studio](https://aistudio.google.com/apikey))

## Instalación

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y pega tu llave:

```
GEMINI_API_KEY=tu_llave
```

El archivo `.env` está en `.gitignore` y no se sube al repositorio.

## Uso

### Interfaz gráfica

```powershell
python interfaz.py
```

Ventana con estilo futurista (tema oscuro con acentos de neón) hecha con `tkinter`, que ya viene con Python. Escribe tu pregunta y presiona Enter o el botón **ENVIAR**.

### Línea de comandos

```powershell
python agente.py "Cuántos planetas hay en el sistema solar?"
```

Si los acentos se ven mal en la consola de Windows, ejecuta antes `$env:PYTHONIOENCODING="utf-8"`.

## Configuración

En `agente.py` e `interfaz.py` puedes cambiar:

- `MODELO`: modelo de Gemini a usar.
- `INSTRUCCIONES`: instrucción de sistema que define el comportamiento del agente.
