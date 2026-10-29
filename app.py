
from flask import Flask
from database import inicializar_db

from routes.inicio import registrar_rutas_inicio
from routes.productos import registrar_rutas_productos
from routes.categorias import registrar_rutas_categorias
from routes.proveedores import registrar_rutas_proveedores
from routes.movimientos import registrar_rutas_movimientos
from routes.reportes import registrar_rutas_reportes

app = Flask(__name__)

app.secret_key = "inventario-clave-temporal-cambiar-antes-de-publicar"


# Inicializar la base de datos
inicializar_db()


# Registrar las rutas de cada módulo
registrar_rutas_inicio(app)
registrar_rutas_productos(app)
registrar_rutas_categorias(app)
registrar_rutas_proveedores(app)
registrar_rutas_movimientos(app)
registrar_rutas_reportes(app)


if __name__ == "__main__":
    app.run(debug=True)