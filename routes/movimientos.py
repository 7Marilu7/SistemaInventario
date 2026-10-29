from flask import render_template, request, redirect, url_for, flash
from database import conectar_db

def registrar_rutas_movimientos(app):

    @app.route("/movimientos")
    def movimientos():
        busqueda = request.args.get("buscar", "").strip()
        tipo_filtro = request.args.get("tipo", "").strip()

        conexion = conectar_db()

        try:
            consulta = """
                SELECT
                    m.id,
                    m.tipo,
                    m.cantidad,
                    m.existencias_anteriores,
                    m.existencias_nuevas,
                    m.motivo,
                    m.notas,
                    m.fecha,
                    p.codigo,
                    p.nombre AS producto
                FROM movimientos m
                INNER JOIN productos p ON p.id = m.producto_id
                WHERE 1 = 1
            """

            parametros = []

            if busqueda:
                consulta += """
                    AND (
                        p.codigo LIKE ?
                        OR p.nombre LIKE ?
                        OR m.motivo LIKE ?
                    )
                """

                termino = f"%{busqueda}%"

                parametros.extend([
                    termino,
                    termino,
                    termino
                ])

            if tipo_filtro in ("entrada", "salida"):
                consulta += " AND m.tipo = ?"
                parametros.append(tipo_filtro)

            consulta += " ORDER BY m.fecha DESC, m.id DESC"

            lista_movimientos = conexion.execute(
                consulta,
                parametros
            ).fetchall()

            return render_template(
                "movimientos.html",
                movimientos=lista_movimientos,
                busqueda=busqueda,
                tipo_filtro=tipo_filtro
            )

        finally:
            conexion.close()

    @app.route("/movimientos/nuevo", methods=["GET", "POST"])
    def nuevo_movimiento():

        conexion = conectar_db()

        try:
            productos = conexion.execute("""
                SELECT id, codigo, nombre, existencias
                FROM productos
                WHERE activo = 1
                ORDER BY nombre COLLATE NOCASE
            """).fetchall()

            if request.method == "POST":

                producto_id = request.form.get("producto_id", "").strip()
                tipo = request.form.get("tipo", "").strip()
                cantidad_texto = request.form.get("cantidad", "").strip()
                motivo = request.form.get("motivo", "").strip()
                notas = request.form.get("notas", "").strip()

                if not producto_id or not cantidad_texto or not motivo:
                    flash(
                        "Completa el producto, la cantidad y el motivo.",
                        "error"
                    )

                    return redirect(url_for("nuevo_movimiento"))

                if tipo not in ("entrada", "salida"):
                    flash("Selecciona un tipo de movimiento válido.", "error")
                    return redirect(url_for("nuevo_movimiento"))

                try:
                    producto_id = int(producto_id)
                    cantidad = int(cantidad_texto)

                    if cantidad <= 0:
                        raise ValueError

                except ValueError:
                    flash(
                        "La cantidad debe ser un número entero mayor que cero.",
                        "error"
                    )

                    return redirect(url_for("nuevo_movimiento"))

                producto = conexion.execute("""
                    SELECT id, existencias
                    FROM productos
                    WHERE id = ? AND activo = 1
                """, (producto_id,)).fetchone()

                if producto is None:
                    flash("El producto seleccionado no existe o está inactivo.", "error")
                    return redirect(url_for("nuevo_movimiento"))

                existencias_anteriores = producto["existencias"]

                if tipo == "entrada":
                    existencias_nuevas = existencias_anteriores + cantidad

                else:
                    if cantidad > existencias_anteriores:
                        flash(
                            f"No hay existencias suficientes. "
                            f"Disponibles: {existencias_anteriores}.",
                            "error"
                        )

                        return redirect(url_for("nuevo_movimiento"))

                    existencias_nuevas = existencias_anteriores - cantidad

                try:
                    with conexion:
                        cursor = conexion.execute("""
                            UPDATE productos
                            SET existencias = ?
                            WHERE id = ?
                              AND activo = 1
                              AND existencias = ?
                        """, (
                            existencias_nuevas,
                            producto_id,
                            existencias_anteriores
                        ))

                        if cursor.rowcount != 1:
                            raise RuntimeError(
                                "Las existencias cambiaron durante la operación."
                            )
                        
                        conexion.execute("""
                            INSERT INTO movimientos (
                                producto_id,
                                tipo,
                                cantidad,
                                existencias_anteriores,
                                existencias_nuevas,
                                motivo,
                                notas
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            producto_id,
                            tipo,
                            cantidad,
                            existencias_anteriores,
                            existencias_nuevas,
                            motivo,
                            notas
                        ))

                    flash(
                        "Movimiento registrado y existencias actualizadas correctamente.",
                        "exito"
                    )

                    return redirect(url_for("movimientos"))

                except Exception:
                    flash(
                        "No se pudo registrar el movimiento. "
                        "No se guardaron cambios parciales.",
                        "error"
                    )

                    return redirect(url_for("nuevo_movimiento"))

            return render_template(
                "movimiento_form.html",
                productos=productos
            )

        finally:
            conexion.close()