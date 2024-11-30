from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3

servicios_bp = Blueprint('servicios', __name__, template_folder='templates')

@servicios_bp.route("/servicios")
def index():
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM servicio")
    servicios = cursor.fetchall()
    conn.close()
    return render_template('index_servicio.html',servicios=servicios)

@servicios_bp.route("/crear_s", methods=["GET", "POST"])
def crear_s():
    if request.method == "POST":
        # Recupera los datos del formulario
        ci_afiliado = request.form["ci_afiliado"]
        fecha_pago_servicio = request.form['fecha_pago_servicio']
        monto = request.form['monto']
        descripcion = request.form['descripcion']
        
        # Inserta los datos en la base de datos
        conn = sqlite3.connect("star_service.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO servicio (ci_afiliado, fecha_pago_servicio, monto, descripcion) 
                VALUES (?, ?, ?, ?)
            """, (ci_afiliado, fecha_pago_servicio, monto, descripcion))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return f"Error al insertar el servicio: {e}"
        finally:
            conn.close()
        
        return redirect(url_for('servicios.index'))
    
    # Obtener afiliados para el formulario
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT ci, nombres FROM afiliado")
    afiliados = cursor.fetchall()
    conn.close()
    
    return render_template("crear_s.html", afiliados=afiliados)


@servicios_bp.route("/editar_s/<int:id>", methods=["GET", "POST"])
def editar_s(id):
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener datos del vehículo a editar
    cursor.execute("SELECT * FROM servicio WHERE id = ?", (id,))
    servicio = cursor.fetchone()

    # Si es POST, actualizar los datos
    if request.method == "POST":
        ci_afiliado = request.form["ci_afiliado"]
        fecha_pago_servicio = request.form['fecha_pago_servicio']
        monto = request.form['monto']
        descripcion = request.form['descripcion']
        
        try:
            cursor.execute("""
                UPDATE servicio 
                SET ci_afiliado = ?, fecha_pago_servicio = ?, monto = ?, descripcion = ?
                WHERE id = ?
            """, (ci_afiliado, fecha_pago_servicio, monto, descripcion, id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return f"Error al actualizar el servicio: {e}"
        finally:
            conn.close()

        return redirect(url_for('servicios.index'))

    # Obtener la lista de afiliados para el formulario
    cursor.execute("SELECT ci, nombres FROM afiliado")
    afiliados = cursor.fetchall()
    conn.close()

    return render_template("editar_s.html", servicio=servicio, afiliados=afiliados)


@servicios_bp.route("/eliminar_s/<int:id>")
def eliminar_s(id):
    conn = sqlite3.connect("star_service.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM servicio WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('servicios.index'))

