from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file,session
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
import sqlite3
import io
from flask import send_file

pagos_bp = Blueprint('pagos',__name__, template_folder = 'templates')


def verifica():
    if 'cargo' not in session or session['cargo'] != "Administrador":
        return False
    return True

#con esta funcion nos conectamos a la base de datos 
def get_db_connection():
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    return conn

# Ruta principal
@pagos_bp.route("/pago")
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM COUTA_MENSUAL ORDER BY fecha DESC")

    pagos = cursor.fetchall()
    conn.close()
    return render_template("index_pago.html", pagos=pagos)

# Crear nuevo pago
@pagos_bp.route("/create")
def create_pago():
    if not verifica():
        return redirect(url_for('pagos.index'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombres, ci FROM afiliado")
    afiliados = cursor.fetchall()
    conn.close()
    return render_template("create.html", afiliados=afiliados)

# Guardar nuevo pago
@pagos_bp.route("/create/save", methods=['POST'])
def save_pago():
    if not verifica():
        return redirect(url_for('pagos.index'))
    ci = request.form['ci']
    fecha = request.form['fecha']
    monto = request.form['monto']
    estado = request.form['estado']
    descripcion = request.form['descripcion']
    mes = request.form['mes']

    # Coneccion a base de datos 
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # condicion si el pago es registrado para el mismo CI y mes
    cursor.execute("""SELECT * FROM COUTA_MENSUAL WHERE ci = ? AND mes = ?""", (ci, mes))
    existing_payment = cursor.fetchone()

    if existing_payment:
        flash("Ya has realizado un pago para este mes. Selecciona otro mes.", "error")
        conn.close()
        return redirect(url_for('pagos.create_pago'))

    cursor.execute("""INSERT INTO COUTA_MENSUAL (ci, monto, estado, fecha, descripcion, mes)
                    VALUES (?, ?, ?, ?, ?, ?)""", (ci, monto, estado, fecha, descripcion, mes))
    conn.commit()
    conn.close()
    return redirect(url_for('pagos.index'))


# Buscar pagos
@pagos_bp.route('/buscar', methods=['GET', 'POST'])
def buscar():
    if request.method == 'POST':
        termino = request.form.get('termino', '')
        if not termino:
            flash("Por favor, ingresa un término de búsqueda.", "danger")
            return redirect(url_for('pagos.buscar'))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM couta_mensual WHERE ci = ? OR cod_pm = ?""", (termino, termino))
        pagos = cursor.fetchall()
        conn.close()
        return render_template('buscar.html', pagos=pagos, termino=termino)
    return render_template('buscar.html', pagos=[], termino='')

# Editar pago
@pagos_bp.route("/edit/<int:cod_pm>")
def edit_pago(cod_pm):
    if not verifica():
        return redirect(url_for('pagos.index'))
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener los datos del pago
    cursor.execute("SELECT * FROM COUTA_MENSUAL WHERE cod_pm = ?", (cod_pm,))
    pago = cursor.fetchone()
    
    if not pago:
        conn.close()
        flash("Pago no encontrado", "danger")
        return redirect(url_for('pagos.index'))

    # Obtener la lista de afiliados
    cursor.execute("SELECT ci, nombres FROM afiliado")
    afiliados = cursor.fetchall()
    conn.close()
    
    return render_template("edit_pago.html", pago=pago, afiliados=afiliados)


# Actualizar pago
@pagos_bp.route("/edit/update/<int:cod_pm>", methods=['POST'])
def update_pago(cod_pm):
    if not verifica():
        return redirect(url_for('pagos.index'))
    ci = request.form['ci']
    fecha = request.form['fecha']
    monto = request.form['monto']
    estado = request.form['estado']
    descripcion = request.form['descripcion']
    mes = request.form['mes']
    
    if not ci or not fecha or not monto or not estado or not descripcion or not mes:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for('pagos.edit_pago', cod_pm=cod_pm))

    # coexiona base de datos 
    conn = get_db_connection()
    cursor = conn.cursor()

    # Evitar que se repita el CI con el mismo mes (excluyendo el registro actual)
    cursor.execute("""
        SELECT * FROM COUTA_MENSUAL
        WHERE ci = ? AND mes = ? AND cod_pm != ?
    """, (ci, mes, cod_pm))
    existing_payment = cursor.fetchone()

    if existing_payment:
        flash("Ya existe un pago registrado para este mes con el mismo CI. Selecciona otro mes.", "error")
        return redirect(url_for('pagos.edit_pago', cod_pm=cod_pm))

    # Obtener los valores actuales del pago antes de hacer la actualización
    cursor.execute("SELECT * FROM COUTA_MENSUAL WHERE cod_pm = ?", (cod_pm,))
    pago_actual = cursor.fetchone()
    if (pago_actual['ci'] == ci and 
        pago_actual['fecha'] == fecha and
        pago_actual['monto'] == monto and
        pago_actual['estado'] == estado and
        pago_actual['descripcion'] == descripcion and
        pago_actual['mes'] == mes):
        # Si no hay cambios, no actualizamos y damos un mensaje
        flash("No se realizaron cambios en el pago.", "warning")
    else:
        cursor.execute("""UPDATE COUTA_MENSUAL SET ci = ?, fecha = ?, monto = ?, estado = ?, descripcion = ?, mes = ? WHERE cod_pm = ?""",
                    (ci, fecha, monto, estado, descripcion, mes, cod_pm))
        conn.commit()
    conn.close()

    return redirect(url_for('pagos.index'))

# Eliminar pago
@pagos_bp.route("/delete/<int:cod_pm>")
def delete_pago(cod_pm):
    if not verifica():
        return redirect(url_for('pagos.index'))
    # Conectamos a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM COUTA_MENSUAL WHERE cod_pm = ?", (cod_pm,))
    pago = cursor.fetchone()

    if pago: 
        cursor.execute("DELETE FROM COUTA_MENSUAL WHERE cod_pm = ?", (cod_pm,))
        conn.commit()
    conn.close()
    return redirect(url_for('pagos.index'))

############################################# GENERAMOS PDF ############################################################

@pagos_bp.route('/reporte_pdf', methods=['GET'])
def generar_reporte_pdf():
    try:
        conn = sqlite3.connect("star_service.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM COUTA_MENSUAL")
        pagos = cursor.fetchall()
        conn.close()

        if not pagos:
            flash("No se encontraron registros para generar el reporte.", "info")
            return redirect(url_for('pagos.index_pago'))

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(letter))
        width, height = landscape(letter)

        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, height - 30, "Reporte de Pagos Mensuales")

        # Cabecera de la tabla
        headers = ["ID", "CI", "Monto", "Mes", "Estado", "Fecha", "Descripción"]
        column_widths = [50, 100, 70, 100, 90, 150, 150]
        x_start = 30
        y_position = height - 60
        row_height = 20

        # Dibujar cabeceras
        c.setFont("Helvetica-Bold", 10)
        x = x_start
        for i, header in enumerate(headers):
            c.drawString(x + 2, y_position, header)
            x += column_widths[i]
        y_position -= row_height

        # Dibujar filas
        c.setFont("Helvetica", 10)
        for pago in pagos:
            if y_position < 50:  # Salto de página
                c.showPage()
                c.setFont("Helvetica-Bold", 12)
                c.drawString(30, height - 30, "Reporte de Pagos Mensuales (Continuación)")
                y_position = height - 60

                # Dibujar cabecera
                c.setFont("Helvetica-Bold", 10)
                x = x_start
                for i, header in enumerate(headers):
                    c.drawString(x + 2, y_position, header)
                    x += column_widths[i]
                y_position -= row_height

            # Datos
            x = x_start
            datos = [pago["cod_pm"], pago["ci"], f"{pago['monto']:.2f}", pago["mes"], pago["estado"], pago["fecha"], pago["descripcion"]]
            for i, dato in enumerate(datos):
                c.drawString(x + 2, y_position, str(dato))
                x += column_widths[i]

            y_position -= row_height

        c.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="reporte_pagos.pdf", mimetype="application/pdf")
    
    except Exception as e:
        flash(f"Error al generar el reporte: {str(e)}", "error")
        return redirect(url_for('pagos.index_pago'))

####################################### REPORTE INDIVIDUAL #############################################################

@pagos_bp.route('/reporte_pdf_busqueda', methods=['GET'])
def generar_reporte_pdf_busqueda():
    try:
        termino = request.args.get('termino', '')

        if not termino:
            flash("Por favor, ingresa un término de búsqueda para generar el reporte.", "info")
            return redirect(url_for('pagos.buscar'))

        conn = sqlite3.connect("star_service.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(""" 
            SELECT * FROM COUTA_MENSUAL
            WHERE ci = ? OR cod_pm = ? 
        """, (termino, termino))
        pagos = cursor.fetchall()
        conn.close()

        if not pagos:
            flash(f"No se encontraron registros para el término '{termino}'.", "info")
            return redirect(url_for('pagos.buscar'))

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(letter))
        width, height = landscape(letter)

        # Centrar el título
        title = f"Reporte de Pagos - Término: {termino}"
        title_width = c.stringWidth(title, "Helvetica-Bold", 12)
        c.setFont("Helvetica-Bold", 12)
        c.drawString((width - title_width) / 2, height - 30, title)

        # Configuración inicial de la tabla
        headers = ["ID", "CI", "Monto", "Mes", "Estado", "Fecha", "Descripción"]
        column_widths = [50, 80, 60, 80, 80, 120, 80]
        total_width = sum(column_widths)
        x_start = (width - total_width) / 2
        y_position = height - 60
        row_height = 18

        # Dibujar cabeceras
        c.setFont("Helvetica-Bold", 10)
        x = x_start
        for header in headers:
            c.drawString(x + 2, y_position, header)
            x += column_widths[headers.index(header)]
        y_position -= row_height

        # Dibujar filas
        c.setFont("Helvetica", 10)
        for pago in pagos:
            if y_position < 50:  # Salto de página
                c.showPage()
                c.setFont("Helvetica-Bold", 12)
                c.drawString((width - title_width) / 2, height - 30, f"Reporte de Pagos - Continuación ({termino})")
                y_position = height - 60

                # Dibujar cabecera
                c.setFont("Helvetica-Bold", 10)
                x = x_start
                for header in headers:
                    c.drawString(x + 2, y_position, header)
                    x += column_widths[headers.index(header)]
                y_position -= row_height

            # Datos
            x = x_start
            datos = [pago["cod_pm"], pago["ci"], f"{pago['monto']:.2f}", pago["mes"], pago["estado"], pago["fecha"], pago["descripcion"]]
            for dato in datos:
                c.drawString(x + 2, y_position, str(dato))
                x += column_widths[datos.index(dato)]

            y_position -= row_height

        c.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="reporte_pagos_busqueda.pdf", mimetype="application/pdf")
    
    except Exception as e:
        flash(f"Error al generar el reporte: {str(e)}", "error")
        return redirect(url_for('pagos.buscar'))

