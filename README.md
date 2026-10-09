# Agente Viáticos

Agente de línea de comandos en Python que envía una pregunta a Gemini (`google-genai`) y muestra la respuesta. Se comporta como asistente de recursos humanos para viáticos, según las instrucciones del archivo `prompts/sistema.md`.

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

Es un chat de varios turnos: el agente recuerda lo dicho antes en la misma conversación (guarda el ID de la interacción anterior y lo envía como `previous_interaction_id`). El botón **NUEVO ↺** borra el panel y empieza una conversación desde cero.

La línea de comandos (`agente.py`) responde una sola pregunta por ejecución, sin memoria.

### Ejecutable (.exe)

Para generar un `AgenteViaticos.exe` de la interfaz gráfica (no requiere consola):

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name AgenteViaticos interfaz.py
```

El ejecutable queda en `dist/AgenteViaticos.exe`. La llave de API no se incluye dentro del .exe: coloca tu archivo `.env` y la carpeta `prompts/` (con `sistema.md`) en la misma carpeta que el ejecutable. Las carpetas `build/` y `dist/` están en `.gitignore`, así que el .exe no se sube al repositorio.

### Línea de comandos

```powershell
python agente.py "Cuántos planetas hay en el sistema solar?"
```

Si los acentos se ven mal en la consola de Windows, ejecuta antes `$env:PYTHONIOENCODING="utf-8"`.

## Configuración

- **Instrucciones del agente:** edita `prompts/sistema.md` (rol, tarifas de alimentación y hotel, tono). Se lee al iniciar, así que no hay que tocar el código. Si el archivo falta, el agente muestra un error. Con el .exe, la carpeta `prompts/` debe estar junto al ejecutable.
- **Modelo:** cambia `MODELO` en `agente.py` e `interfaz.py`.
