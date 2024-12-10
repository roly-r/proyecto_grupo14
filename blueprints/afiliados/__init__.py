import sqlite3
from flask import Flask,redirect,render_template,url_for,request,Blueprint,session, flash, send_file
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
import sqlite3

from functools import wraps
#proporciona la capacidad de manipular archivo en memoria
import io 

afiliados_bp = Blueprint('afiliados', __name__, template_folder='templates')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id_user' not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def verifica():
    if 'cargo' not in session or session['cargo'] != "Administrador":
        return False
    return True

@afiliados_bp.route("/afiliados")
@login_required
def index():
    conn=sqlite3.connect("star_service.db")
    conn.row_factory=sqlite3.Row

    cur=conn.cursor()
    cur.execute("SELECT * FROM afiliado ORDER BY fecha_incorporacion DESC")
    afiliados=cur.fetchall()
    return render_template("index_afiliado.html",afiliados=afiliados)

@afiliados_bp.route("/detalle/<int:ci>")
@login_required
def detalle_afiliado(ci):
    conn = sqlite3.connect("star_service.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Datos del afiliado
    cur.execute("SELECT * FROM afiliado WHERE ci = ?", (ci,))
    afiliado = cur.fetchone()

    # Vehículo(s) del afiliado
    cur.execute("SELECT * FROM vehiculo WHERE ci_afiliado = ?", (ci,))
    vehiculos = cur.fetchall()

    # Ingresos del afiliado
    cur.execute("SELECT * FROM ingreso WHERE ci_afiliado = ?", (ci,))
    ingresos = cur.fetchall()

    # Cuotas mensuales del afiliado
    cur.execute("SELECT * FROM COUTA_MENSUAL WHERE ci = ?", (ci,))
    cuotas = cur.fetchall()

    total_cuotas = sum([cuota['monto'] for cuota in cuotas])

    conn.close()

    return render_template(
        "detalle_afiliado.html",
        afiliado=afiliado,
        vehiculos=vehiculos,
        ingresos=ingresos,
        cuotas=cuotas,
        total_cuotas=total_cuotas
    )


@afiliados_bp.route("/crear_afiliado")
@login_required
def afiliado_crear():
    if not verifica():
        return redirect(url_for('afiliados.index'))  # Redirige a la página principal si no es administrador
    return render_template("crear_afi.html")

@afiliados_bp.route("/crear/guarda",methods=['POST'])
@login_required
def afiliado_sv():
    if not verifica():
        return redirect(url_for('afiliados.index'))
    ci=request.form['ci']
    nombres=request.form['nombres']
    apellidos=request.form['apellidos']
    direccion=request.form['direccion']
    fecha_nacimiento=request.form['fecha_nacimiento']
    telefono=request.form['telefono']
    fecha_incorporacion=request.form['fecha_incorporacion']
    nro_licencia=request.form['nro_licencia']

    conn=sqlite3.connect("star_service.db")
    cur=conn.cursor()

    cur.execute("INSERT INTO afiliado (ci,nombres,apellidos,direccion,fecha_nacimiento,telefono,fecha_incorporacion,nro_licencia) VALUES (?,?,?,?,?,?,?,?)",
                                      (ci,nombres,apellidos,direccion,fecha_nacimiento,telefono,fecha_incorporacion,nro_licencia))

    conn.commit()
    conn.close()
    return redirect(url_for('afiliados.index'))

@afiliados_bp.route("/edit/<int:ci>")
@login_required
def afiliado_edit(ci):
    if not verifica():
        return redirect(url_for('afiliados.index'))
    conn=sqlite3.connect("star_service.db")
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("SELECT * FROM afiliado WHERE ci=?",(ci,))
    afiliado=cur.fetchone()
    conn.close()
    return render_template("editar_afi.html",afiliado=afiliado)

@afiliados_bp.route("/update",methods=['POST'])
@login_required
def afiliados_update():
    if not verifica():
        return redirect(url_for('afiliados.index'))
    ci=request.form['ci']
    nombres=request.form['nombres']
    apellidos=request.form['apellidos']
    direccion=request.form['direccion']
    fecha_nacimiento=request.form['fecha_nacimiento']
    telefono=request.form['telefono']
    fecha_incorporacion=request.form['fecha_incorporacion']
    nro_licencia=request.form['nro_licencia']

    conn=sqlite3.connect("star_service.db")
    cu=conn.cursor()

    cu.execute("UPDATE afiliado SET nombres=?,apellidos=?,direccion=?,fecha_nacimiento=?,telefono=?,fecha_incorporacion=?,nro_licencia=? WHERE ci=?",
               (nombres,apellidos,direccion,fecha_nacimiento,telefono,fecha_incorporacion,nro_licencia,ci))

    conn.commit()
    conn.close()
    return redirect(url_for('afiliados.index'))

# Buscar pagos

@afiliados_bp.route('/buscar_afi', methods=['GET', 'POST'])
@login_required
def buscar_afi():
    if request.method == 'POST':
        termino = request.form.get('termino', '')
        if not termino:
            flash("Por favor, ingresa un término de búsqueda.", "danger")
            return redirect(url_for('afiliados.buscar_afi'))

        conn = sqlite3.connect("star_service.db")
        conn.row_factory = sqlite3.Row  # Importante para acceder por nombre
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM afiliado WHERE ci = ? OR nombres = ?""", (termino, termino))
        afiliados = cursor.fetchall()
        conn.close()
        return render_template('buscar_afi.html', afiliados=afiliados, termino=termino)
    return render_template('buscar_afi.html', afiliados=[], termino='')



@afiliados_bp.route("/borrar/<int:ci>")
@login_required
def afiliados_del(ci):
    if not verifica():
        return redirect(url_for('afiliados.index'))
    conn=sqlite3.connect("star_service.db")
    cur=conn.cursor()

    cur.execute("DELETE FROM afiliado WHERE ci=?",(ci,))
    conn.commit()
    conn.close()
    return redirect(url_for('afiliados.index'))

####################################### REPORTE INDIVIDUAL #############################################################

@afiliados_bp.route('/reporte_detalle/<int:ci>', methods=['GET'])
@login_required
def generar_reporte_detalle(ci):
    try:
        # Conectar a la base de datos para obtener los datos del afiliado
        conn = sqlite3.connect("star_service.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT * FROM afiliado WHERE ci = ?", (ci,))
        afiliado = cur.fetchone()

        cur.execute("SELECT * FROM vehiculo WHERE ci_afiliado = ?", (ci,))
        vehiculos = cur.fetchall()

        cur.execute("SELECT * FROM ingreso WHERE ci_afiliado = ?", (ci,))
        ingresos = cur.fetchall()

        cur.execute("SELECT * FROM COUTA_MENSUAL WHERE ci = ?", (ci,))
        cuotas = cur.fetchall()
        total_cuotas = sum([cuota['monto'] for cuota in cuotas])  # Calcular el total de cuotas
        conn.close()

        if not afiliado:
            flash("No se encontró al afiliado con el CI proporcionado.", "error")
            return redirect(url_for('afiliados.index'))

        # Crear el PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Encabezado del reporte
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 50, "STAR SERVICE")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, height - 70, "Teléfono: 591 77771234")
        c.drawCentredString(width / 2, height - 85, "Correo: star_service@gmail.com")
        c.drawCentredString(width / 2, height - 100, "Sede: La Paz-Bolivia / AV. Satelite")

        # Título del reporte
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, height - 140, f"Reporte Detallado - {afiliado['nombres']} {afiliado['apellidos']}")

        # Datos del afiliado
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 180, "DATOS DEL AFILIADO:")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 200, f"Nombres: {afiliado['nombres']} {afiliado['apellidos']}")
        c.drawString(50, height - 220, f"CI: {afiliado['ci']}")
        c.drawString(50, height - 240, f"Dirección: {afiliado['direccion']}")
        c.drawString(50, height - 260, f"Fecha de Nacimiento: {afiliado['fecha_nacimiento']}")
        c.drawString(50, height - 280, f"Teléfono: {afiliado['telefono']}")
        c.drawString(50, height - 300, f"Fecha de Incorporación: {afiliado['fecha_incorporacion']}")
        c.drawString(50, height - 320, f"Número de Licencia: {afiliado['nro_licencia']}")

        y = height - 360

        # Datos de vehículos
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "VEHICULO REGISTRADO:")
        y -= 20
        if vehiculos:
            c.setFont("Helvetica", 10)
            for vehiculo in vehiculos:
                c.drawString(50, y, f"Marca: {vehiculo['marca']}")
                c.drawString(200, y, f"Modelo: {vehiculo['modelo']}")
                y -= 15
                c.drawString(50, y, f"Color: {vehiculo['color']}")
                c.drawString(200, y, f"Placa: {vehiculo['placa']}")
                y -= 30
                if y < 50:  # Salto de página
                    c.showPage()
                    y = height - 50
        else:
            c.setFont("Helvetica", 10)
            c.drawString(50, y, "No hay vehículos registrados.")
            y -= 20

        # Ingresos (en tabla)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "PAGO DE INGRESO:")
        y -= 20
        if ingresos:
            c.setFont("Helvetica", 10)
            c.drawString(50, y, "Monto       Estado       Fecha")
            y -= 15
            for ingreso in ingresos:
                c.drawString(50, y, f"{ingreso['monto']:<12} {ingreso['estado']:<12} {ingreso['fecha']}")
                y -= 15
                if y < 50:  # Salto de página
                    c.showPage()
                    y = height - 50
            c.setFont("Helvetica-Bold", 12)
            y -= 20
            c.drawString(50, y, f"Pago de Ingreso: {ingreso['monto']:<12} Bs.")
        else:
            c.setFont("Helvetica", 10)
            c.drawString(50, y, "No hay ingresos registrados.")
            y -= 20

        y -= 30

        # Cuotas Mensuales (en tabla)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "CUOTAS MENSUALES:")
        y -= 20
        if cuotas:
            c.setFont("Helvetica", 10)
            c.drawString(50, y, "Monto       Estado       Fecha            Mes")
            y -= 15
            for cuota in cuotas:
                c.drawString(50, y, f"{cuota['monto']:<12} {cuota['estado']:<12} {cuota['fecha']:<12} {cuota['mes']}")
                y -= 15
                if y < 50:  # Salto de página
                    c.showPage()
                    y = height - 50
            # Total de Cuotas
            c.setFont("Helvetica-Bold", 12)
            y -= 20
            c.drawString(50, y, f"Total de Cuotas Mensuales: {total_cuotas} Bs.")
            y -= 20
        else:
            c.setFont("Helvetica", 10)
            c.drawString(50, y, "No hay cuotas registradas.")
            y -= 20

        # Guardar el PDF
        c.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"detalle_afiliado_{afiliado['ci']}.pdf", mimetype="application/pdf")

    except Exception as e:
        flash(f"Error al generar el reporte: {str(e)}", "error")
        return redirect(url_for('afiliados.index'))

