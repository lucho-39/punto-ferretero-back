
from componentes.vistas_web import *
from componentes.vistas_api import *
from componentes.vistas_web import registrar_rutas_web
from componentes.vistas_api import registrar_rutas
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

registrar_rutas_web(app)
registrar_rutas(app)

app.json.ensure_ascii = False

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


if __name__ == "__main__":
    app.run()
