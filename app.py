from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

# Crear la aplicación Flask
app = Flask(__name__)
app.secret_key = "clave_secreta"

@app.route('/categoria/<nombre>')
def categoria(nombre):
    # Filtrar productos por categoría
    productos_filtrados = [p for p in productos if nombre.lower() in p["nombre"].lower()]

    # Si no hay productos, mostrar mensaje
    if not productos_filtrados:
        return render_template("catalogo.html", categoria=nombre, productos=[], mensaje="No se encontraron resultados.")

    return render_template("catalogo.html", categoria=nombre, productos=productos_filtrados)



# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Contador de intentos
intentos = 0
MAX_INTENTOS = 3

class Usuario(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return Usuario(user_id)

# Lista de productos (ejemplo)
productos = [
    {"nombre": "Laptop Gamer", "precio": "", "imagen": "laptop.png"},
    {"nombre": "Monitores", "precio": "", "imagen": "monitor.webp"},
    {"nombre": "Procesador", "precio": "", "imagen": "procesador.png"},
    {"nombre": "Tarjeta Gráfica", "precio": "", "imagen": "grafica.png"},
]

# Página principal
@app.route('/')
def inicio():
    return render_template('index.html', productos=productos)

# Login con 3 intentos
@app.route('/login', methods=['GET', 'POST'])
def login():
    global intentos
    if request.method == 'POST':
        nombre = request.form['username']
        clave = request.form['password']

        # Bloqueo si excede intentos
        if intentos >= MAX_INTENTOS:
            return render_template('bloqueo.html')

        # Validación usuario/clave desde archivo usuarios.txt
        try:
            with open("usuarios.txt", "r", encoding="utf-8") as archivo:
                for linea in archivo:
                    datos = linea.strip().split(",")
                    if datos[0] == nombre and datos[1] == clave:
                        user = Usuario(nombre)
                        login_user(user)
                        intentos = 0
                        flash("✅ Inicio de sesión exitoso", "success")
                        return redirect(url_for('inicio'))
                else:
                    intentos += 1
                    restantes = MAX_INTENTOS - intentos
                    flash(f"❌ Usuario o contraseña incorrectos — Intentos restantes: {restantes}", "danger")
        except FileNotFoundError:
            flash("⚠️ No existe el archivo de usuarios.", "danger")

    return render_template('login.html')

# Registro de usuarios
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    mensaje = ""
    usuario = ""
    clave = ""

    if request.method == 'POST':
        accion = request.form.get("accion")
        usuario = request.form.get("usuario")
        clave = request.form.get("clave")

        # Guardar en usuarios.txt
        if accion == "guardar":
            with open("usuarios.txt", "a", encoding="utf-8") as archivo:
                archivo.write(f"{usuario},{clave}\n")
            mensaje = "✅ Usuario registrado correctamente."

        # Buscar en usuarios.txt
        elif accion == "buscar":
            try:
                with open("usuarios.txt", "r", encoding="utf-8") as archivo:
                    for linea in archivo:
                        datos = linea.strip().split(",")
                        if datos[0] == usuario:
                            clave = datos[1]
                            mensaje = f"🔍 Usuario encontrado: {usuario}"
                            break
                    else:
                        mensaje = "⚠️ Usuario no encontrado."
            except FileNotFoundError:
                mensaje = "❌ No existe el archivo de usuarios."

    return render_template("registro.html", mensaje=mensaje, usuario=usuario, clave=clave)

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("👋 Sesión cerrada", "info")
    return redirect(url_for('inicio'))
@app.route("/envios")
def envios():
    return render_template("envios.html")


# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)

    
