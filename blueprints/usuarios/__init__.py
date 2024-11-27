from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

usuarios_bp = Blueprint('usuarios', __name__, template_folder='templates')


# Ruta para mostrar el listado 
@usuarios_bp.route("/usuarios")
def index_user():
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuario")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template('index_user.html',usuarios=usuarios)

# Ruta para crear 
@usuarios_bp.route("/crear_user", methods=["GET", "POST"])
def crear_user():
    if request.method == "POST":
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        ci = request.form['ci']
        tipo = request.form['tipo']
        fecha_nan = request.form['fecha_nan']
        fecha_inc = request.form['fecha_inc']
        username = request.form['username']
        password = request.form['password']

        password_encriptado =  generate_password_hash(password)
        
        conn = sqlite3.connect("star_service.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuario (nombre,apellido,ci,tipo,fecha_nan,fecha_inc,username,password) 
            VALUES (?,?,?,?,?,?,?,?)
        """, (nombre,apellido,ci,tipo,fecha_nan,fecha_inc,username,password_encriptado))
        conn.commit()
        conn.close()
        
        return redirect(url_for('usuarios.index_user'))
    return render_template("crear_user.html")

# Ruta para editar 
@usuarios_bp.route("/editar_user/<int:id_user>", methods=["GET", "POST"])
def editar_user(id_user):
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuario WHERE id_user = ?", (id_user,))
    usuario = cursor.fetchone()
    
    if request.method == "POST":
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        ci = request.form['ci']
        tipo = request.form['tipo']
        fecha_nan = request.form['fecha_nan']
        fecha_inc = request.form['fecha_inc']
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute("""
            UPDATE usuario 
            SET nombre=?,apellido=?,ci=?,tipo=?,fecha_nan=?,fecha_inc=?,username=?,password=?  
            WHERE id_user = ?
        """, (nombre,apellido,ci,tipo,fecha_nan,fecha_inc,username,password, id_user))
        conn.commit()
        conn.close()
        return redirect(url_for('usuarios.index_user'))
     
    conn.close()
    return render_template("editar_user.html", usuario=usuario)

# Ruta para eliminar 
@usuarios_bp.route("/eliminar_user/<int:id_user>")
def eliminar_user(id_user):
    conn = sqlite3.connect("star_service.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuario WHERE id_user = ?", (id_user,))
    conn.commit()
    conn.close()
    return redirect(url_for('usuarios.index_user'))
