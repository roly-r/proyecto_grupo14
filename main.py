from flask import Flask, render_template,session,request,redirect
from blueprints.vehiculos import vehiculos_bp
from blueprints.afiliados import afiliados_bp
from blueprints.servicios import servicios_bp
from blueprints.usuarios import usuarios_bp
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps

app = Flask(__name__)

app.secret_key = 'miclavesecreta'

app.register_blueprint(vehiculos_bp)
app.register_blueprint(afiliados_bp)
app.register_blueprint(servicios_bp)
app.register_blueprint(usuarios_bp)

@app.route("/")
def home():
    return render_template("index.html")

def init_database():
    conn = sqlite3.connect("star_service.db")
    cursor = conn.cursor()
    
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS afiliado(
        ci INTEGER PRIMARY KEY,
        nombres TEXT NOT NULL,
        apellidos TEXT NOT NULL,
        direccion TEXT NOT NULL,
        fecha_nacimiento DATE NOT NULL,
        telefono INTEGER NOT NULL,
        fecha_incorporacion DATE NOT NULL,
        nro_licencia TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehiculo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ci_afiliado INT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            color TEXT NOT NULL,
            numero_chasis TEXT UNIQUE NOT NULL,
            placa TEXT UNIQUE NOT NULL,
            observaciones TEXT,
            FOREIGN KEY (ci_afiliado) REFERENCES afiliado(ci)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servicio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ci_afiliado INT,
            fecha_pago_servicio DATE NOT NULL,
            monto DECIMAL(10, 2),
            descripcion TEXT,
            FOREIGN KEY (ci_afiliado) REFERENCES afiliado(ci)
        )
    """)
    
    cursor.execute(
       """
        CREATE TABLE IF NOT EXISTS usuario(
            id_user INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            ci INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            fecha_nan DATE NOT NULL,
            fecha_inc DATE NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
        """)

    conn.commit()
    conn.close()

init_database()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id_user' not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
    
@app.route("/login",methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn =  sqlite3.connect("star_service.db")
        # Permite obtener registros como diccionario
        conn.row_factory =  sqlite3.Row
        cursor =  conn.cursor()
        cursor.execute("SELECT * FROM usuario WHERE username = ?",(username,))
        usuario = cursor.fetchone()
        conn.close()
        
        if usuario and check_password_hash(usuario['password'],password):
            session['id_user'] = usuario['id_user']
            return redirect('/admin/dashboard')
                
    return render_template('auth/login.html')
    
@app.route("/logout")
def logout():
    session.pop('id_user',None)
    return redirect("/")
    
@app.route("/admin/dashboard")
@login_required
def dashboard():
    return render_template('admin/dashboard.html')



if __name__ == "__main__":
    app.run(debug=True)