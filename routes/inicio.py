from flask import render_template
from database import conectar_db

def registrar_rutas_inicio(app):

    @app.route("/")
    def inicio():
        conexion = conectar_db()

        try:
            total_productos = conexion.execute("""
                SELECT COUNT(*)
                FROM productos
                WHERE activo = 1
            """).fetchone()[0]

            total_unidades = conexion.execute("""
                SELECT COALESCE(SUM(existencias), 0)
                FROM productos
                WHERE activo = 1
            """).fetchone()[0]

            stock_bajo = conexion.execute("""
                SELECT COUNT(*)
                FROM productos
                WHERE activo = 1
                  AND existencias > 0
                  AND existencias <= stock_minimo
            """).fetchone()[0]

            productos_agotados = conexion.execute("""
                SELECT COUNT(*)
                FROM productos
                WHERE activo = 1
                  AND existencias = 0
            """).fetchone()[0]

            movimientos = conexion.execute("""
                SELECT
                    m.id,
                    m.tipo,
                    m.cantidad,
                    m.existencias_anteriores,
                    m.existencias_nuevas,
                    m.motivo,
                    m.fecha,
                    p.codigo,
                    p.nombre AS producto
                FROM movimientos AS m
                INNER JOIN productos AS p
                    ON p.id = m.producto_id
                ORDER BY m.id DESC
                LIMIT 8
            """).fetchall()

            return render_template(
                "index.html",
                total_productos=total_productos,
                total_unidades=total_unidades,
                stock_bajo=stock_bajo,
                productos_agotados=productos_agotados,
                movimientos=movimientos
            )

        finally:
            conexion.close()