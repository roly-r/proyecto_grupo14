import sqlite3
from flask import Flask,redirect,render_template,url_for,request,Blueprint
#producto(id : integer, descripcion: texto, cantidad:integer, precio:float)
afiliados_bp = Blueprint('afiliados', __name__, template_folder='templates')


@afiliados_bp.route("/afiliados")
def index():
    conn=sqlite3.connect("star_service.db")
    conn.row_factory=sqlite3.Row

    cur=conn.cursor()
    cur.execute("SELECT * FROM afiliado")
    afiliados=cur.fetchall()
    return render_template("index_afiliado.html",afiliados=afiliados)

@afiliados_bp.route("/crear_afiliado")
def afiliado_crear():
    return render_template("crear_afi.html")

@afiliados_bp.route("/crear/guarda",methods=['POST'])
def afiliado_sv():
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
def afiliado_edit(ci):
    conn=sqlite3.connect("star_service.db")
    conn.row_factory=sqlite3.Row
    cur=conn.cursor()

    cur.execute("SELECT * FROM afiliado WHERE ci=?",(ci,))
    afiliado=cur.fetchone()
    conn.close()
    return render_template("editar_afi.html",afiliado=afiliado)

@afiliados_bp.route("/update",methods=['POST'])
def afiliados_update():
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

@afiliados_bp.route("/borrar/<int:ci>")
def afiliados_del(ci):
    conn=sqlite3.connect("star_service.db")
    cur=conn.cursor()

    cur.execute("DELETE FROM afiliado WHERE ci=?",(ci,))
    conn.commit()
    conn.close()
    return redirect(url_for('afiliados.index'))

