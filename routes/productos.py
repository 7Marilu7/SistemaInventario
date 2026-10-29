from flask import render_template, request, redirect, url_for, flash
from database import conectar_db

def registrar_rutas_productos(app):

    @app.route("/productos")
    def productos():
        busqueda = request.args.get("buscar", "").strip()
        conexion = conectar_db()

        try:
            consulta = """
                SELECT
                    p.*,
                    c.nombre AS categoria,
                    pr.nombre AS proveedor
                FROM productos AS p
                LEFT JOIN categorias AS c
                    ON c.id = p.categoria_id
                LEFT JOIN proveedores AS pr
                    ON pr.id = p.proveedor_id
                WHERE p.activo = 1
            """
            parametros = []

            if busqueda:
                consulta += """
                    AND (
                        p.codigo LIKE ?
                        OR p.nombre LIKE ?
                    )
                """
                termino = f"%{busqueda}%"
                parametros.extend([termino, termino])

            consulta += " ORDER BY p.nombre COLLATE NOCASE"

            lista_productos = conexion.execute(
                consulta, parametros
            ).fetchall()

            return render_template(
                "productos.html",
                productos=lista_productos,
                busqueda=busqueda
            )

        finally:
            conexion.close()

    @app.route("/productos/nuevo", methods=["GET", "POST"])
    def nuevo_producto():
        conexion = conectar_db()

        try:
            categorias = conexion.execute("""
                SELECT id, nombre
                FROM categorias
                WHERE activa = 1
                ORDER BY nombre
            """).fetchall()

            proveedores = conexion.execute("""
                SELECT id, nombre
                FROM proveedores
                WHERE activo = 1
                ORDER BY nombre
            """).fetchall()

            if request.method == "POST":
                codigo = request.form.get("codigo", "").strip()
                nombre = request.form.get("nombre", "").strip()
                descripcion = request.form.get("descripcion", "").strip()
                categoria_id = request.form.get("categoria_id", "").strip()
                proveedor_id = request.form.get("proveedor_id", "").strip()
                precio_costo_texto = request.form.get("precio_costo", "").strip()
                precio_venta_texto = request.form.get("precio_venta", "").strip()
                existencias_texto = request.form.get("existencias", "0").strip()
                stock_minimo_texto = request.form.get("stock_minimo", "0").strip()

                if not codigo or not nombre:
                    flash(
                        "El código y el nombre son obligatorios.",
                        "error"
                    )
                    return redirect(url_for("nuevo_producto"))

                try:
                    precio_costo = float(precio_costo_texto or 0)
                    precio_venta = float(precio_venta_texto or 0)
                    existencias = int(existencias_texto or 0)
                    stock_minimo = int(stock_minimo_texto or 0)

                    if (
                        precio_costo < 0
                        or precio_venta < 0
                        or existencias < 0
                        or stock_minimo < 0
                    ):
                        raise ValueError

                except ValueError:
                    flash(
                        "Verifica los precios y las cantidades. "
                        "No se permiten valores negativos ni "
                        "formatos incorrectos.",
                        "error"
                    )
                    return redirect(url_for("nuevo_producto"))

                try:
                    with conexion:
                        cursor = conexion.execute("""
                            INSERT INTO productos (
                                codigo,
                                nombre,
                                descripcion,
                                categoria_id,
                                proveedor_id,
                                precio_costo,
                                precio_venta,
                                existencias,
                                stock_minimo
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            codigo,
                            nombre,
                            descripcion,
                            int(categoria_id) if categoria_id else None,
                            int(proveedor_id) if proveedor_id else None,
                            precio_costo,
                            precio_venta,
                            existencias,
                            stock_minimo
                        ))

                        if existencias > 0:
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
                                VALUES (?, 'entrada', ?, 0, ?, ?, ?)
                            """, (
                                cursor.lastrowid,
                                existencias,
                                existencias,
                                "Inventario inicial",
                                "Existencias al registrar el producto"
                            ))

                    flash(
                        "Producto registrado correctamente.",
                        "exito"
                    )
                    return redirect(url_for("productos"))

                except Exception as error:
                    if (
                        "UNIQUE constraint failed: productos.codigo"
                        in str(error)
                    ):
                        flash(
                            "Ya existe un producto con ese código. "
                            "Utiliza un código diferente.",
                            "error"
                        )
                    else:
                        flash(
                            "No se pudo registrar el producto. "
                            "Revisa los datos e inténtalo nuevamente.",
                            "error"
                        )

                    return redirect(url_for("nuevo_producto"))

            return render_template(
                "producto_form.html",
                producto=None,
                categorias=categorias,
                proveedores=proveedores,
                titulo="Registrar producto"
            )

        finally:
            conexion.close()

    @app.route("/productos/editar/<int:producto_id>", methods=["GET", "POST"])
    def editar_producto(producto_id):
        conexion = conectar_db()

        try:
            producto = conexion.execute("""
                SELECT *
                FROM productos
                WHERE id = ? AND activo = 1
            """, (producto_id,)).fetchone()

            if producto is None:
                flash(
                    "El producto no existe o está desactivado.",
                    "error"
                )
                return redirect(url_for("productos"))

            categorias = conexion.execute("""
                SELECT id, nombre
                FROM categorias
                WHERE activa = 1 OR id = ?
                ORDER BY nombre
            """, (producto["categoria_id"] or 0,)).fetchall()

            proveedores = conexion.execute("""
                SELECT id, nombre
                FROM proveedores
                WHERE activo = 1 OR id = ?
                ORDER BY nombre
            """, (producto["proveedor_id"] or 0,)).fetchall()

            if request.method == "POST":
                codigo = request.form.get("codigo", "").strip()
                nombre = request.form.get("nombre", "").strip()
                descripcion = request.form.get("descripcion", "").strip()
                categoria_id = request.form.get("categoria_id", "").strip()
                proveedor_id = request.form.get("proveedor_id", "").strip()

                try:
                    precio_costo = float(request.form.get("precio_costo", "0").strip() or 0)
                    precio_venta = float(request.form.get("precio_venta", "0").strip() or 0)
                    stock_minimo = int(request.form.get("stock_minimo", "0").strip() or 0)

                    if (
                        precio_costo < 0
                        or precio_venta < 0
                        or stock_minimo < 0
                    ):
                        raise ValueError

                except ValueError:
                    flash(
                        "Verifica los precios y el stock mínimo.",
                        "error"
                    )
                    return redirect(
                        url_for(
                            "editar_producto",
                            producto_id=producto_id
                        )
                    )

                if not codigo or not nombre:
                    flash(
                        "El código y el nombre son obligatorios.",
                        "error"
                    )
                    return redirect(
                        url_for(
                            "editar_producto",
                            producto_id=producto_id
                        )
                    )

                try:
                    with conexion:
                        conexion.execute("""
                            UPDATE productos
                            SET codigo = ?,
                                nombre = ?,
                                descripcion = ?,
                                categoria_id = ?,
                                proveedor_id = ?,
                                precio_costo = ?,
                                precio_venta = ?,
                                stock_minimo = ?
                            WHERE id = ? AND activo = 1
                        """, (
                            codigo,
                            nombre,
                            descripcion,
                            int(categoria_id) if categoria_id else None,
                            int(proveedor_id) if proveedor_id else None,
                            precio_costo,
                            precio_venta,
                            stock_minimo,
                            producto_id
                        ))

                    flash(
                        "Producto actualizado correctamente.",
                        "exito"
                    )
                    return redirect(url_for("productos"))

                except Exception:
                    flash(
                        "No se pudo actualizar. Comprueba que el "
                        "código no esté asignado a otro producto.",
                        "error"
                    )
                    return redirect(
                        url_for(
                            "editar_producto",
                            producto_id=producto_id
                        )
                    )

            return render_template(
                "producto_form.html",
                producto=producto,
                categorias=categorias,
                proveedores=proveedores,
                titulo="Editar producto"
            )

        finally:
            conexion.close()

    @app.route("/productos/desactivar/<int:producto_id>",methods=["POST"])
    def desactivar_producto(producto_id):
        conexion = conectar_db()

        try:
            with conexion:
                cursor = conexion.execute("""
                    UPDATE productos
                    SET activo = 0
                    WHERE id = ? AND activo = 1
                """, (producto_id,))

            if cursor.rowcount:
                flash(
                    "Producto desactivado correctamente.",
                    "exito"
                )
            else:
                flash(
                    "No se encontró el producto solicitado.",
                    "error"
                )

        finally:
            conexion.close()

        return redirect(url_for("productos"))
    
    @app.route("/productos/desactivados")
    def productos_desactivados():
        busqueda = request.args.get("buscar", "").strip()
        conexion = conectar_db()

        try:
            consulta = """
                SELECT
                    p.*,
                    c.nombre AS categoria,
                    pr.nombre AS proveedor
                FROM productos AS p
                LEFT JOIN categorias AS c
                    ON c.id = p.categoria_id
                LEFT JOIN proveedores AS pr
                    ON pr.id = p.proveedor_id
                WHERE p.activo = 0
            """
            parametros = []

            if busqueda:
                consulta += """
                    AND (
                        p.codigo LIKE ?
                        OR p.nombre LIKE ?
                    )
                """
                termino = f"%{busqueda}%"
                parametros.extend([termino, termino])

            consulta += " ORDER BY p.nombre COLLATE NOCASE"

            lista_productos = conexion.execute(consulta, parametros).fetchall()

            return render_template(
                "productos_desactivados.html",
                productos=lista_productos,
                busqueda=busqueda
            )

        finally:
            conexion.close()

    @app.route("/productos/reactivar/<int:producto_id>", methods=["POST"])
    def reactivar_producto(producto_id):
        conexion = conectar_db()

        try:
            with conexion:
                cursor = conexion.execute("""
                    UPDATE productos
                    SET activo = 1
                    WHERE id = ? AND activo = 0
                """, (producto_id,))

            if cursor.rowcount:
                flash(
                    "Producto reactivado correctamente.",
                    "exito"
                )
            else:
                flash(
                    "No se encontró el producto desactivado.",
                    "error"
                )

        finally:
            conexion.close()

        return redirect(url_for("productos_desactivados"))