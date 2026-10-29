import sqlite3
from pathlib import Path

# Carpeta principal del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Ruta de la base de datos
DATABASE = BASE_DIR / "inventario.db"


def conectar_db():
    """Abre una conexión con la base de datos SQLite."""
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def inicializar_db():
    """Crea las tablas necesarias si todavía no existen."""

    conexion = conectar_db()

    try:
        with conexion:
            # Tabla de categorías
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    descripcion TEXT DEFAULT '',
                    activa INTEGER NOT NULL DEFAULT 1
                )
            """)

            # Tabla de proveedores
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS proveedores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    telefono TEXT DEFAULT '',
                    correo TEXT DEFAULT '',
                    direccion TEXT DEFAULT '',
                    observaciones TEXT DEFAULT '',
                    activo INTEGER NOT NULL DEFAULT 1
                )
            """)

            # Tabla de productos
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT NOT NULL UNIQUE,
                    nombre TEXT NOT NULL,
                    descripcion TEXT DEFAULT '',
                    categoria_id INTEGER,
                    proveedor_id INTEGER,
                    precio_costo REAL NOT NULL DEFAULT 0,
                    precio_venta REAL NOT NULL DEFAULT 0,
                    existencias INTEGER NOT NULL DEFAULT 0,
                    stock_minimo INTEGER NOT NULL DEFAULT 0,
                    activo INTEGER NOT NULL DEFAULT 1,
                    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (categoria_id)
                        REFERENCES categorias(id)
                        ON DELETE RESTRICT,

                    FOREIGN KEY (proveedor_id)
                        REFERENCES proveedores(id)
                        ON DELETE RESTRICT,

                    CHECK (precio_costo >= 0),
                    CHECK (precio_venta >= 0),
                    CHECK (existencias >= 0),
                    CHECK (stock_minimo >= 0)
                )
            """)

            # Tabla de movimientos de inventario
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS movimientos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    producto_id INTEGER NOT NULL,
                    tipo TEXT NOT NULL,
                    cantidad INTEGER NOT NULL,
                    existencias_anteriores INTEGER NOT NULL,
                    existencias_nuevas INTEGER NOT NULL,
                    motivo TEXT NOT NULL,
                    notas TEXT DEFAULT '',
                    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (producto_id)
                        REFERENCES productos(id)
                        ON DELETE RESTRICT,

                    CHECK (tipo IN ('entrada', 'salida')),
                    CHECK (cantidad > 0),
                    CHECK (existencias_anteriores >= 0),
                    CHECK (existencias_nuevas >= 0)
                )
            """)

            # Tabla de usuarios: se utilizará para el inicio de sesión
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    usuario TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    rol TEXT NOT NULL DEFAULT 'administrador',
                    activo INTEGER NOT NULL DEFAULT 1,
                    fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Configuración personalizable del sistema
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS configuracion (
                    clave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                )
            """)

            # Valores iniciales de configuración
            valores_iniciales = [
                ("nombre_sistema", "Sistema de Inventario"),
                ("nombre_negocio", "Mi Negocio"),
                ("moneda", "MXN"),
                ("tema", "oscuro"),
                ("color_principal", "#FFD21F")
            ]

            conexion.executemany("""
                INSERT OR IGNORE INTO configuracion (clave, valor)
                VALUES (?, ?)
            """, valores_iniciales)

            # Índices para acelerar búsquedas y reportes
            conexion.execute("""
                CREATE INDEX IF NOT EXISTS idx_productos_nombre
                ON productos(nombre)
            """)

            conexion.execute("""
                CREATE INDEX IF NOT EXISTS idx_movimientos_fecha
                ON movimientos(fecha)
            """)

            conexion.execute("""
                CREATE INDEX IF NOT EXISTS idx_movimientos_producto
                ON movimientos(producto_id)
            """)

        print("Base de datos inicializada correctamente.")

    finally:
        conexion.close()


if __name__ == "__main__":
    inicializar_db()