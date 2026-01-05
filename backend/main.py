from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Prueba TFG</title>
        </head>
        <body>
            <h1>Hola, esto es una prueba</h1>
            <p>Mi TFG de psicología + IA</p>
        </body>
    </html>
    """
