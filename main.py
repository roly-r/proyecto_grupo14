from flask import Flask, render_template
from blueprints.vehiculos import vehiculos_bp
import sqlite3

app = Flask(__name__)

# Registrar los blueprints
app.register_blueprint(vehiculos_bp, url_prefix="/vehiculos")


# Ruta principal
@app.route("/")
def home():
    return render_template("index.html")


# Crear la base de datos
def init_database():
    conn = sqlite3.connect("star_service.db")
    cursor = conn.cursor()
    # Crear tabla de vehículos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehiculo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            modelo TEXT NOT NULL,
            color TEXT NOT NULL,
            numero_chasis TEXT UNIQUE NOT NULL,
            placa TEXT UNIQUE NOT NULL,
            observaciones TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Inicializar la base de datos al arrancar la aplicación
init_database()

if __name__ == "__main__":
    app.run(debug=True)
