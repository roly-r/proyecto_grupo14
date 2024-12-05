from flask import Blueprint, render_template, request, redirect, url_for,session
import sqlite3

ingresos_bp = Blueprint('ingresos', __name__, template_folder='templates')

def verifica():
    if 'cargo' not in session or session['cargo'] != "Administrador":
        return False
    return True

@ingresos_bp.route("/ingresos")
def index_ingreso():
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingreso")
    ingresos = cursor.fetchall()
    cursor.execute("SELECT SUM(monto) as total_monto FROM ingreso")
    total_monto = cursor.fetchone()["total_monto"] or 0 

    conn.close()
    return render_template('index_ingreso.html',ingresos=ingresos, total_monto=total_monto)

@ingresos_bp.route("/crear_i", methods=["GET", "POST"])
def crear_i():
    if not verifica():
        return redirect(url_for('ingresos.index_ingreso'))
    if request.method == "POST":
        # Recupera los datos del formulario
        ci_afiliado = request.form["ci_afiliado"]
        monto = request.form['monto']
        estado = request.form['estado']
        fecha = request.form['fecha']
        observaciones = request.form['observaciones']
        
        # Inserta los datos en la base de datos
        conn = sqlite3.connect("star_service.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO ingreso (ci_afiliado, monto, estado, fecha, observaciones) 
                VALUES (?, ?, ?, ?, ?)
            """, (ci_afiliado, monto, estado, fecha, observaciones))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return f"Error al insertar. {e}"
        finally:
            conn.close()
        
        return redirect(url_for('ingresos.index_ingreso'))
    
    # Obtener afiliados para el formulario
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT ci, nombres FROM afiliado")
    afiliados = cursor.fetchall()
    conn.close()
    
    return render_template("crear_i.html", afiliados=afiliados)


@ingresos_bp.route("/editar_i/<int:id>", methods=["GET", "POST"])
def editar_i(id):
    if not verifica():
        return redirect(url_for('ingresos.index_ingreso'))
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener datos del vehículo a editar
    cursor.execute("SELECT * FROM ingreso WHERE id = ?", (id,))
    ingreso = cursor.fetchone()

    # Si es POST, actualizar los datos
    if request.method == "POST":
        ci_afiliado = request.form["ci_afiliado"]
        monto = request.form['monto']
        estado = request.form['estado']
        fecha = request.form['fecha']
        observaciones = request.form['observaciones']
        
        try:
            cursor.execute("""
                UPDATE ingreso 
                SET ci_afiliado = ?, monto = ?, estado = ?, fecha = ?, observaciones = ?
                WHERE id = ?
            """, (ci_afiliado, monto, estado, fecha, observaciones, id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return f"Error al actualizar el ingreso: {e}"
        finally:
            conn.close()

        return redirect(url_for('ingresos.index_ingreso'))

    # Obtener la lista de afiliados para el formulario
    cursor.execute("SELECT ci, nombres FROM afiliado")
    afiliados = cursor.fetchall()
    conn.close()

    return render_template("editar_i.html", ingreso=ingreso, afiliados=afiliados)


@ingresos_bp.route("/eliminar_i/<int:id>")
def eliminar_i(id):
    if not verifica():
        return redirect(url_for('ingresos.index_ingreso'))
    conn = sqlite3.connect("star_service.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ingreso WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('ingresos.index_ingreso'))

