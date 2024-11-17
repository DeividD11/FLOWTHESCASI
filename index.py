from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required

# Models:
from models.ModelUser import ModelUser

# Entities:
from models.entities.User import User

app = Flask(__name__)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Flowthes'

# Clave secreta
app.secret_key = 'mysecretkey'

mysql = MySQL(app)

login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(mysql, id)

@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User(0, request.form['correo'], request.form['contraseña'])
        logged_user = ModelUser.login(mysql, user)
        if logged_user is not None:
            if logged_user.Contraseña:
                return redirect(url_for('home'))
            else:
                flash('Contraseña incorrecta')
                return render_template('login.html')
        else:
            flash('Usuario o Contraseña no encontrados')
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('inicio'))

@app.route('/home')
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

def status_401(error):
    return redirect(url_for('login'))

def status_404(error):
    return "<h1>Página no encontrada</h1>", 404

@app.route('/registro')
def registro():
    return render_template('registro.html')

@app.route('/Datos', methods=['POST'])
def datos():
    if request.method == 'POST':
        nombre = request.form['nombres']
        apellido = request.form['apellidos']
        tipoDoc = request.form['tipoDocumento']
        numDoc = request.form['N°Documento']
        fechaNacimiento = request.form['fechaNacimiento']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        cur = mysql.connection.cursor()
        try:
            cur.execute('INSERT INTO Usuario (N°Identificacion, Nombres, Apellidos, TipoDocumento, FechaNacimiento, Correo, Contraseña) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (numDoc, nombre, apellido, tipoDoc, fechaNacimiento, correo, contraseña))
            mysql.connection.commit()
            flash('Usuario registrado correctamente')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al registrar el usuario: {e}')
        finally:
            cur.close()

        return redirect(url_for('login'))

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

        if not nombre or not unidades or not precio or not talla or not cantidad_minima or not clasificacion:
            flash('Todos los campos son obligatorios')
            return redirect(url_for('registrar_producto'))

        try:
            unidades = int(unidades)
            precio = float(precio)
            cantidad_minima = int(cantidad_minima)

            cur = mysql.connection.cursor()

            cur.execute("""
                INSERT INTO producto (NombreProducto, UnidadesEnExistencia, PrecioPorUnidad, Talla, CantidadMinima, Clasificacion) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, unidades, precio, talla, cantidad_minima, clasificacion))

            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
        finally:
            cur.close()

        return redirect(url_for('registrar_producto'))

@app.route('/detalle_producto')
def detalle_producto():
    return render_template('detalle_producto.html')

if __name__ == '__main__':
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True)


