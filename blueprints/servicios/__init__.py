from flask import Blueprint, render_template, request, redirect, url_for,session
import sqlite3

servicios_bp = Blueprint('servicios', __name__, template_folder='templates')

def verifica():
    if 'cargo' not in session or session['cargo'] != "Administrador":
        return False
    return True

@servicios_bp.route("/servicios")
def index_s():
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Consulta con LEFT JOIN para mostrar servicios y datos de vehículos
    cursor.execute("""
    SELECT servicio.id, servicio.fecha_pago_servicio, servicio.monto, servicio.descripcion, 
           vehiculo.placa, vehiculo.marca
    FROM servicio
    LEFT JOIN vehiculo ON servicio.id_vehiculo = vehiculo.id ORDER BY fecha_pago_servicio DESC
    """)
    servicios = cursor.fetchall()
    
    cursor.execute("SELECT SUM(monto) as total_monto FROM servicio")
    total_monto = cursor.fetchone()["total_monto"] or 0 

    
    conn.close()

    return render_template('index_servicio.html', servicios=servicios, total_monto=total_monto)


@servicios_bp.route("/crear_s", methods=["GET", "POST"])
def crear_s():
    
    if request.method == "POST":
        # Recupera los datos del formulario
        id_vehiculo = request.form.get("id_vehiculo")
        fecha_pago_servicio = request.form['fecha_pago_servicio']
        monto = request.form['monto']
        descripcion = request.form['descripcion']
        
        # Inserta los datos en la base de datos
        conn = sqlite3.connect("star_service.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO servicio (id_vehiculo, fecha_pago_servicio, monto, descripcion) 
                VALUES (?, ?, ?, ?)
            """, (id_vehiculo, fecha_pago_servicio, monto, descripcion))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return f"Error al insertar el servicio: {e}"
        finally:
            conn.close()
        
        return redirect(url_for('servicios.index_s'))
    
    # Obtener vehículos para el formulario
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, placa, marca FROM vehiculo")
    vehiculos = cursor.fetchall()
    conn.close()
    
    return render_template("crear_s.html", vehiculos=vehiculos)


@servicios_bp.route("/editar_s/<int:id>", methods=["GET", "POST"])
def editar_s(id):
    
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener datos del servicio a editar
    cursor.execute("SELECT * FROM servicio WHERE id = ?", (id,))
    servicio = cursor.fetchone()

    if request.method == "POST":
        id_vehiculo = request.form.get("id_vehiculo")
        fecha_pago_servicio = request.form['fecha_pago_servicio']
        monto = request.form['monto']
        descripcion = request.form['descripcion']
        
        try:
            cursor.execute("""
                UPDATE servicio 
                SET id_vehiculo = ?, fecha_pago_servicio = ?, monto = ?, descripcion = ?
                WHERE id = ?
            """, (id_vehiculo, fecha_pago_servicio, monto, descripcion, id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return f"Error al actualizar el servicio: {e}"
        finally:
            conn.close()

        return redirect(url_for('servicios.index_s'))

    # Obtener la lista de vehículos para el formulario
    cursor.execute("SELECT id, placa, marca FROM vehiculo")
    vehiculos = cursor.fetchall()
    conn.close()

    return render_template("editar_s.html", servicio=servicio, vehiculos=vehiculos)


@servicios_bp.route("/eliminar_s/<int:id>")
def eliminar_s(id):
    
    conn = sqlite3.connect("star_service.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM servicio WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('servicios.index_s'))
