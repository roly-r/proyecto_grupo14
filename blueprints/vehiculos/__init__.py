from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

vehiculos_bp = Blueprint('vehiculos', __name__, template_folder='templates')

# Función para obtener todos los vehículos de la base de datos
# def get_all_vehiculos():
#     conn = sqlite3.connect("star_service.db")
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM vehiculo")
#     vehiculos = cursor.fetchall()
#     conn.close()
#     return vehiculos

# Ruta para mostrar el listado de vehículos
@vehiculos_bp.route("/")
def index():
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehiculo")
    vehiculos = cursor.fetchall()
    conn.close()
    return render_template('index_vehiculo.html',vehiculos=vehiculos)

# Ruta para crear un nuevo vehículo
@vehiculos_bp.route("/crear", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        marca = request.form['marca']
        modelo = request.form['modelo']
        color = request.form['color']
        numero_chasis = request.form['numero_chasis']
        placa = request.form['placa']
        observaciones = request.form['observaciones']
        
        conn = sqlite3.connect("star_service.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vehiculo (marca, modelo, color, numero_chasis, placa, observaciones) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (marca, modelo, color, numero_chasis, placa, observaciones))
        conn.commit()
        conn.close()
        
        return redirect(url_for('vehiculos.index'))
    return render_template("crear.html")

# Ruta para editar un vehículo
@vehiculos_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehiculo WHERE id = ?", (id,))
    vehiculo = cursor.fetchone()
    
    if request.method == "POST":
        marca = request.form['marca']
        modelo = request.form['modelo']
        color = request.form['color']
        numero_chasis = request.form['numero_chasis']
        placa = request.form['placa']
        observaciones = request.form['observaciones']
        
        cursor.execute("""
            UPDATE vehiculo 
            SET marca = ?, modelo = ?, color = ?, numero_chasis = ?, placa = ?, observaciones = ? 
            WHERE id = ?
        """, (marca, modelo, color, numero_chasis, placa, observaciones, id))
        conn.commit()
        conn.close()
        return redirect(url_for('vehiculos.index'))
    
    conn.close()
    return render_template("editar.html", vehiculo=vehiculo)

# Ruta para eliminar un vehículo
@vehiculos_bp.route("/eliminar/<int:id>")
def eliminar(id):
    conn = sqlite3.connect("star_service.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vehiculo WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('vehiculos.index'))
