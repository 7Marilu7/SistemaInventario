from flask import render_template, request, redirect, url_for, flash
from database import conectar_db

def registrar_rutas_proveedores(app):

    @app.route("/proveedores")
    def proveedores():
        busqueda = request.args.get("buscar", "").strip()
        conexion = conectar_db()

        try:
            consulta = """
                SELECT *
                FROM proveedores
                WHERE activo = 1
            """
            parametros = []

            if busqueda:
                consulta += """
                    AND (
                        nombre LIKE ?
                        OR telefono LIKE ?
                        OR correo LIKE ?
                    )
                """
                termino = f"%{busqueda}%"
                parametros.extend([termino, termino, termino])

            consulta += " ORDER BY nombre COLLATE NOCASE"

            lista_proveedores = conexion.execute(consulta, parametros).fetchall()

            return render_template(
                "proveedores.html",
                proveedores=lista_proveedores,
                busqueda=busqueda
            )

        finally:
            conexion.close()

    @app.route("/proveedores/nuevo", methods=["GET", "POST"])
    def nuevo_proveedor():
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            telefono = request.form.get("telefono", "").strip()
            correo = request.form.get("correo", "").strip()
            direccion = request.form.get("direccion", "").strip()
            observaciones = request.form.get("observaciones", "").strip()

            if not nombre:
                flash("El nombre del proveedor es obligatorio.", "error")
                return redirect(url_for("nuevo_proveedor"))

            conexion = conectar_db()

            try:
                with conexion:
                    conexion.execute("""
                        INSERT INTO proveedores (
                            nombre,
                            telefono,
                            correo,
                            direccion,
                            observaciones
                        )
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        nombre,
                        telefono,
                        correo,
                        direccion,
                        observaciones
                    ))

                flash("Proveedor registrado correctamente.", "exito")
                return redirect(url_for("proveedores"))

            except Exception:
                flash(
                    "No se pudo registrar el proveedor. Revisa los datos.",
                    "error"
                )
                return redirect(url_for("nuevo_proveedor"))

            finally:
                conexion.close()

        return render_template(
            "proveedor_form.html",
            proveedor=None,
            titulo="Registrar proveedor"
        )

    @app.route("/proveedores/editar/<int:proveedor_id>", methods=["GET", "POST"])
    def editar_proveedor(proveedor_id):
        conexion = conectar_db()

        try:
            proveedor = conexion.execute("""
                SELECT *
                FROM proveedores
                WHERE id = ? AND activo = 1
            """, (proveedor_id,)).fetchone()

            if proveedor is None:
                flash("El proveedor no existe o está desactivado.", "error")
                return redirect(url_for("proveedores"))

            if request.method == "POST":
                nombre = request.form.get("nombre", "").strip()
                telefono = request.form.get("telefono", "").strip()
                correo = request.form.get("correo", "").strip()
                direccion = request.form.get("direccion", "").strip()
                observaciones = request.form.get(
                    "observaciones", ""
                ).strip()

                if not nombre:
                    flash("El nombre del proveedor es obligatorio.", "error")
                    return redirect(
                        url_for("editar_proveedor", proveedor_id=proveedor_id)
                    )

                with conexion:
                    conexion.execute("""
                        UPDATE proveedores
                        SET nombre = ?,
                            telefono = ?,
                            correo = ?,
                            direccion = ?,
                            observaciones = ?
                        WHERE id = ? AND activo = 1
                    """, (
                        nombre,
                        telefono,
                        correo,
                        direccion,
                        observaciones,
                        proveedor_id
                    ))

                flash("Proveedor actualizado correctamente.", "exito")
                return redirect(url_for("proveedores"))

            return render_template(
                "proveedor_form.html",
                proveedor=proveedor,
                titulo="Editar proveedor"
            )

        finally:
            conexion.close()

    @app.route("/proveedores/desactivar/<int:proveedor_id>", methods=["POST"])
    def desactivar_proveedor(proveedor_id):
        conexion = conectar_db()

        try:
            productos_asociados = conexion.execute("""
                SELECT COUNT(*)
                FROM productos
                WHERE proveedor_id = ? AND activo = 1
            """, (proveedor_id,)).fetchone()[0]

            if productos_asociados > 0:
                flash(
                    "No puedes desactivar este proveedor porque tiene "
                    "productos activos asociados.",
                    "error"
                )
                return redirect(url_for("proveedores"))

            with conexion:
                cursor = conexion.execute("""
                    UPDATE proveedores
                    SET activo = 0
                    WHERE id = ? AND activo = 1
                """, (proveedor_id,))

            if cursor.rowcount:
                flash("Proveedor desactivado correctamente.", "exito")
            else:
                flash("No se encontró el proveedor solicitado.", "error")

        finally:
            conexion.close()

        return redirect(url_for("proveedores"))