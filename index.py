import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb
import re
from MySQLdb import IntegrityError

# Models:
from models.ModelUser import ModelUser

# Entities:
from models.entities.User import User

app = Flask(__name__)

# Configuración de la base de datos con variables de entorno
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'Flowthes')

# Clave secreta con variable de entorno para mayor seguridad
app.secret_key = os.getenv('FLASK_SECRET_KEY')
if not app.secret_key:
    raise ValueError("La variable de entorno FLASK_SECRET_KEY no está configurada")

mysql = MySQL(app)

# Configuración de Flask-Login
login_manager_app = LoginManager(app)
login_manager_app.login_view = 'login'  # Redirigir a la página de login si no está autenticado

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql, id)

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        user = User(0, request.form['correo'], request.form['contraseña'])
        logged_user = ModelUser.login(mysql, user)

        if logged_user is not None and check_password_hash(logged_user.Contraseña, user.contraseña):
            login_user(logged_user)
            return redirect(url_for('home'))
        else:
            flash('Usuario o Contraseña no encontrados')

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('inicio'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/realizacion')
def realizacion():
    return render_template('realizacion.html')

@app.route('/carrito')
def carrito():
    return render_template('carrito.html')

@app.route('/factura')
def factura():
    return render_template('factura.html')

@app.route('/protected')
@login_required
def protected():
    return "<h1>Esta es una vista protegida, solo para usuarios autenticados.</h1>"

@app.errorhandler(401)
def status_401(error):
    return redirect(url_for('login'))

@app.errorhandler(404)
def status_404(error):
    return render_template('404.html'), 404

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombres']
        apellido = request.form['apellidos']
        tipoDoc = request.form['tipoDocumento']
        numDoc = request.form['N°Documento']
        fechaNacimiento = request.form['fechaNacimiento']
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        if not all([nombre, apellido, tipoDoc, numDoc, fechaNacimiento, correo, contraseña]):
            flash('Todos los campos son obligatorios')
            return render_template('registro.html')

        # Validación de correo electrónico
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            flash('Correo electrónico inválido')
            return render_template('registro.html')

        # Validación de contraseña (mínimo 8 caracteres)
        if len(contraseña) < 8:
            flash('La contraseña debe tener al menos 8 caracteres')
            return render_template('registro.html')

        hashed_password = generate_password_hash(contraseña)

        try:
            with mysql.connection.cursor() as cur:
                cur.execute('INSERT INTO Usuario (N°Identificacion, Nombres, Apellidos, TipoDocumento, FechaNacimiento, Correo, Contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                            (numDoc, nombre, apellido, tipoDoc, fechaNacimiento, correo, hashed_password))
                mysql.connection.commit()
            flash('Usuario registrado correctamente')
        except IntegrityError as e:
            mysql.connection.rollback()
            flash('Error de integridad: clave duplicada o datos incorrectos.')
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            app.logger.error(f"Error de base de datos: {e}")
            flash("Ha ocurrido un error al procesar la solicitud.")
        except Exception as e:
            mysql.connection.rollback()
            app.logger.error(f"Error desconocido: {e}")
            flash("Ha ocurrido un error inesperado.")

        return redirect(url_for('login'))

    return render_template('registro.html')

def validar_producto(nombre, unidades, precio, talla, cantidad_minima, clasificacion):
    if not all([nombre, unidades, precio, talla, cantidad_minima, clasificacion]):
        return False, 'Todos los campos son obligatorios'
    try:
        unidades = int(unidades)
        precio = float(precio)
        cantidad_minima = int(cantidad_minima)
        return True, ''
    except ValueError:
        return False, 'Las unidades, precio y cantidad mínima deben ser números válidos'

@app.route('/producto')
def registrar_producto():
    return render_template('producto.html')

@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        unidades = request.form.get('unidades')
        precio = request.form.get('precio')
        talla = request.form.get('talla')
        cantidad_minima = request.form.get('cantidad_minima')
        clasificacion = request.form.get('clasificacion')

        is_valid, error_message = validar_producto(nombre, unidades, precio, talla, cantidad_minima, clasificacion)
        if not is_valid:
            flash(error_message)
            return redirect(url_for('registrar_producto'))

        try:
            with mysql.connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO producto (NombreProducto, UnidadesEnExistencia, PrecioPorUnidad, Talla, CantidadMinima, Clasificacion) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nombre, unidades, precio, talla, cantidad_minima, clasificacion))
                mysql.connection.commit()
            flash('Producto registrado correctamente')
        except MySQLdb.Error as e:
            mysql.connection.rollback()
            app.logger.error(f"Error de base de datos: {e}")
            flash('Error de base de datos: Por favor, intenta nuevamente.')
        except Exception as e:
            mysql.connection.rollback()
            app.logger.error(f"Error desconocido: {e}")
            flash('Error desconocido. Intenta nuevamente.')

        return redirect(url_for('registrar_producto'))

@app.route('/detalle_producto')
def detalle_producto():
    return render_template('detalle_producto.html')

if __name__ == '__main__':
    app.run(debug=True)
