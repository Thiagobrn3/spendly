# 💰 Spendly - Aplicación de Finanzas Personales

**Spendly** es una aplicación web para el **seguimiento de finanzas personales**, desarrollada con **Django** y **Bootstrap 5**.  
Permite a los usuarios **registrarse, iniciar sesión y administrar sus cuentas, transacciones, tarjetas de crédito, presupuestos y gastos recurrentes**, todo desde un panel moderno e intuitivo.

---

## 🚀 Características Principales

- 🔐 **Autenticación de usuarios:** Registro, inicio y cierre de sesión completos.  
- 📊 **Dashboard interactivo:** Resumen de saldo total, gráficos de gastos por categoría (*Chart.js*) y listado de cuentas y tarjetas.  
- 💼 **Gestión de cuentas:** Crea múltiples cuentas (bancarias, efectivo, etc.) con actualización automática de saldos.  
- 💸 **CRUD de transacciones:** Alta, baja, modificación y consulta de ingresos o gastos.  
- 💳 **Gestión de tarjetas de crédito:** Cálculo automático del saldo a pagar según la fecha de cierre.  
- 🎯 **Presupuestos mensuales:** Define límites de gasto por categoría.  
- 🔁 **Transacciones recurrentes:** Registra ingresos o gastos fijos como sueldos o suscripciones.  
- 🖤 **Interfaz moderna y responsive:** Estilo oscuro con diseño adaptativo usando Bootstrap 5.

---

## 🧩 Requisitos Previos

Antes de comenzar, asegurate de tener instalado:

- **Python 3.10** o superior  
- **Git**

---

## ⚙️ Instalación y Configuración

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/thiagobrn3/spendly.git
cd spendly
```

---

### 2️⃣ Crear y activar un entorno virtual

#### En macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### En Windows:
```bash
python -m venv venv
.
env\Scripts ctivate
```

---

### 3️⃣ Instalar dependencias

Crea un archivo `requirements.txt` en la raíz del proyecto con este contenido:

```
Django
crispy-forms
crispy-bootstrap5
python-dotenv
python-dateutil
```

Luego instalá los paquetes necesarios:

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configurar variables de entorno

Crea un archivo `.env` en la carpeta raíz (donde está `manage.py`) con el siguiente contenido:

```
SECRET_KEY='TU_SECRET_KEY_AQUI'
DEBUG=True
```

> 💡 Puedes generar una nueva `SECRET_KEY` desde un generador online de *Django Secret Key*.

---

### 5️⃣ Aplicar migraciones

Esto creará la base de datos `db.sqlite3` con todas las tablas necesarias.

```bash
python manage.py migrate
```

---

### 6️⃣ Crear un superusuario

Para acceder al panel de administración de Django:

```bash
python manage.py createsuperuser
```

---

## ▶️ Ejecución

Inicia el servidor de desarrollo con:

```bash
python manage.py runserver
```

Luego abrí tu navegador y visitá:  
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 👨‍💻 Autor

**Thiago Barrionuevo**  
GitHub: [@thiagobrn3](https://github.com/thiagobrn3)
