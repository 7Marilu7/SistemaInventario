from flask import render_template, request, redirect, url_for, flash
from database import conectar_db

def registrar_rutas_categorias(app):

    @app.route("/categorias")
    def categorias():
        busqueda = request.args.get("buscar", "").strip()
        conexion = conectar_db()

        try:
            consulta = """
                SELECT *
                FROM categorias
                WHERE activa = 1
            """
            parametros = []

            if busqueda:
                consulta += " AND nombre LIKE ?"
                parametros.append(f"%{busqueda}%")

            consulta += " ORDER BY nombre COLLATE NOCASE"

            lista_categorias = conexion.execute(consulta, parametros).fetchall()

            return render_template(
                "categorias.html",
                categorias=lista_categorias,
                busqueda=busqueda
            )

        finally:
            conexion.close()

    @app.route("/categorias/nueva", methods=["GET", "POST"])
    def nueva_categoria():
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            descripcion = request.form.get("descripcion", "").strip()

            if not nombre:
                flash("El nombre de la categoría es obligatorio.", "error")
                return redirect(url_for("nueva_categoria"))

            conexion = conectar_db()

            try:
                with conexion:
                    conexion.execute("""
                        INSERT INTO categorias (nombre, descripcion)
                        VALUES (?, ?)
                    """, (nombre, descripcion))

                flash("Categoría registrada correctamente.", "exito")
                return redirect(url_for("categorias"))

            except Exception as error:
                if "UNIQUE constraint failed" in str(error):
                    flash("Ya existe una categoría con ese nombre.", "error")
                else:
                    flash("No se pudo registrar la categoría.", "error")

                return redirect(url_for("nueva_categoria"))

            finally:
                conexion.close()

        return render_template(
            "categoria_form.html",
            categoria=None,
            titulo="Registrar categoría"
        )

    @app.route("/categorias/editar/<int:categoria_id>", methods=["GET", "POST"])
    def editar_categoria(categoria_id):
        conexion = conectar_db()

        try:
            categoria = conexion.execute("""
                SELECT *
                FROM categorias
                WHERE id = ? AND activa = 1
            """, (categoria_id,)).fetchone()

            if categoria is None:
                flash("La categoría no existe o está desactivada.", "error")
                return redirect(url_for("categorias"))

            if request.method == "POST":
                nombre = request.form.get("nombre", "").strip()
                descripcion = request.form.get("descripcion", "").strip()

                if not nombre:
                    flash("El nombre de la categoría es obligatorio.", "error")
                    return redirect(
                        url_for("editar_categoria", categoria_id=categoria_id)
                    )

                try:
                    with conexion:
                        conexion.execute("""
                            UPDATE categorias
                            SET nombre = ?, descripcion = ?
                            WHERE id = ? AND activa = 1
                        """, (nombre, descripcion, categoria_id))

                    flash("Categoría actualizada correctamente.", "exito")
                    return redirect(url_for("categorias"))

                except Exception:
                    flash(
                        "No se pudo actualizar. Comprueba que el nombre "
                        "no esté utilizado por otra categoría.",
                        "error"
                    )
                    return redirect(
                        url_for("editar_categoria", categoria_id=categoria_id)
                    )

            return render_template(
                "categoria_form.html",
                categoria=categoria,
                titulo="Editar categoría"
            )

        finally:
            conexion.close()

    @app.route("/categorias/desactivar/<int:categoria_id>", methods=["POST"])
    def desactivar_categoria(categoria_id):
        conexion = conectar_db()

        try:
            productos_asociados = conexion.execute("""
                SELECT COUNT(*)
                FROM productos
                WHERE categoria_id = ? AND activo = 1
            """, (categoria_id,)).fetchone()[0]

            if productos_asociados > 0:
                flash(
                    "No puedes desactivar esta categoría porque tiene "
                    "productos activos asociados.",
                    "error"
                )
                return redirect(url_for("categorias"))

            with conexion:
                cursor = conexion.execute("""
                    UPDATE categorias
                    SET activa = 0
                    WHERE id = ? AND activa = 1
                """, (categoria_id,))

            if cursor.rowcount:
                flash("Categoría desactivada correctamente.", "exito")
            else:
                flash("No se encontró la categoría solicitada.", "error")

        finally:
            conexion.close()

        return redirect(url_for("categorias"))