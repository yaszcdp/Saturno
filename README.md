# Proyecto Saturno 
## Administrador de Negocios.

Saturno es un sistema de gestión comercial que permite la administración de Comprobantes (Ventas, Compras y Pagos), Caja Registradora, Productos, Clientes, Proveedores y sus Cuentas Corrientes.
Este proyecto está construido usando Django, con una arquitectura modular que facilita la expansión y el mantenimiento.

## Despliegue en Python Anywhere

https://echidnamun.pythonanywhere.com/

## Video del proyecto en loom. 

https://www.loom.com/share/9dea6cb6f668403a957e6a9a7f09f4a8?sid=0a55433a-7673-492a-8e4d-17874981ce96
 
## Tabla de Contenidos
- [Características Principales](#características-principales)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Configuración del proyecto](#configuración-del-proyecto)
- [Uso](#uso)
  
## Características Principales

- **Gestión de Usuarios**: Administración de roles y permisos (Vendedor, Cajero, SuperAdmin).
- **Comprobantes/Tickets**: Creación y manejo de tickets para ventas, compras y pagos, con la posibilidad de agregar múltiples ítems.
- **Caja Registradora**: Gestión de la apertura y cierre de caja, vinculada a las operaciones del día.
- **Productos**: Administración de un catálogo de productos.
- **Clientes y Proveedores**: Manejo de cuentas corrientes para clientes y proveedores, con estados de cuenta y registro de operaciones.

Cada una de estas entidades tiene sus propias vistas y formularios para gestionar la información de manera eficiente.

## Tecnologías Utilizadas

- **Python 3.12**
- **Django 5.1**
- **SQLite** (Base de datos por defecto)
- **HTML5, CSS, Bootstrap** (Frontend)

## Configuración del proyecto

1. Clonar el repositorio:
    ```bash
    git clone https://github.com/yaszcdp/Proyecto-Saturno.git
    cd Proyecto-Saturno
    code .
    ```

2. Aplicar las migraciones y ejecutar el servidor de desarrollo:
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

3. Acceder a la aplicación en el navegador en `http://127.0.0.1:8000` o `http://localhost:8000/`.

## Uso

**Acceder al Panel de Administración:**
  Dirígete a `http://127.0.0.1:8000/user/login/` o accede desde el botón en el index e inicia sesión con las credenciales del superusuario.
  ```bash
    user: master
    password: Roberto7$
  ```

**Crear y Gestionar Tickets:**
  Usa la interfaz para generar tickets de ventas, compras o pagos, y administra los ítems relacionados.

**Manejo de Caja Registradora:**
  Abre y cierra cajas diarias, vinculando los movimientos de la jornada.

**Administrar Productos, Clientes y Proveedores:**
  Gestiona el catálogo de productos, y maneja las cuentas corrientes de clientes y proveedores.


## Casos de Uso

[Ver casos de uso](media/casos_de_uso.pdf)
