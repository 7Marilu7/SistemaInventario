# Sistema de Inventario

Aplicación web para la gestión y el control de inventario de un negocio, desarrollada con Python, Flask y SQLite.

## Descripción

Sistema de Inventario es una aplicación web diseñada para facilitar la administración de productos, categorías y proveedores, así como el control de entradas y salidas de mercancía. Permite consultar las existencias disponibles, identificar productos con stock mínimo y generar reportes de inventario.

## Funcionalidades

- Gestión de productos.
- Administración de categorías.
- Administración de proveedores.
- Registro de movimientos de inventario (entradas y salidas).
- Consulta de existencias disponibles.
- Control de stock mínimo.
- Generación de reportes de inventario.
- Administración de usuarios y configuración del sistema.

## Tecnologías utilizadas

- Python
- Flask
- SQLite
- HTML5
- CSS3
- openpyxl

## Estructura del proyecto

```text
SistemaInventario/
├── routes/
├── static/
├── templates/
├── app.py
├── database.py
├── requirements
├── .gitignore
└── README.md

## Instalación local

1. Instala Python 3.

2. Clona este repositorio:

```bash
git clone https://github.com/7Marilu7/SistemaInventario.git
```

3. Accede a la carpeta del proyecto:

```bash
cd SistemaInventario
```

4. Crea un entorno virtual:

```bash
python -m venv .venv
```

5. Activa el entorno virtual en Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

En Linux o macOS:

```bash
source .venv/bin/activate
```

6. Instala las dependencias:

```bash
python -m pip install -r requirements
```

7. Ejecuta la aplicación:

```bash
python app.py
```

8. Abre en tu navegador:

`http://127.0.0.1:5000`

La base de datos SQLite se inicializa automáticamente al ejecutar la aplicación.

## Base de datos

El sistema utiliza SQLite para almacenar la información de productos, categorías, proveedores, movimientos de inventario, usuarios y configuración.

El archivo `inventario.db` se genera automáticamente en la carpeta principal del proyecto cuando se inicializa la base de datos.

## Estado del proyecto

Proyecto desarrollado como parte de un portafolio personal para demostrar conocimientos en desarrollo web y gestión de bases de datos.

## Autoría

Desarrollado por **María Guadalupe Cruz Paz**.

[GitHub](https://github.com/7Marilu7)
