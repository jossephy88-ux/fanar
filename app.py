from flask import Flask, render_template, request, jsonify, send_file, session, redirect
import sqlite3, os, json
from datetime import datetime
import openpyxl

app = Flask(__name__)
app.secret_key = "fanar_seguridad"

DB = "fanar.db"
EXPORTS = "exports"


# ───────────────── DATABASE ─────────────────

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            password TEXT
        )
        """)
        db.execute(
            "INSERT OR IGNORE INTO usuarios (usuario,password) VALUES ('admin','1234')"
        )
        db.execute("""
        CREATE TABLE IF NOT EXISTS motos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT,
            chasis TEXT,
            cliente TEXT,
            cedula TEXT,
            fecha TEXT,
            observaciones TEXT,
            periodo TEXT,
            creado TEXT
        )
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT,
            chasis TEXT,
            cliente TEXT,
            cedula TEXT,
            fecha TEXT,
            motor TEXT,
            marca_modelo TEXT,
            observaciones TEXT,
            periodo TEXT,
            creado TEXT
        )
        """)
        db.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            periodo TEXT,
            tipo TEXT,
            datos TEXT,
            exportado TEXT
        )
        """)
    os.makedirs(EXPORTS, exist_ok=True)


# Inicializar siempre al arrancar
init_db()


# ───────────────── UTIL ─────────────────

def periodo_actual():
    return datetime.now().strftime("%Y-%m")


# ───────────────── LOGIN ─────────────────

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]
        with get_db() as db:
            user = db.execute(
                "SELECT * FROM usuarios WHERE usuario=? AND password=?",
                (usuario,password)
            ).fetchone()
        if user:
            session["usuario"] = usuario
            return redirect("/")
        return "Usuario o contraseña incorrecta"
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ───────────────── PÁGINAS ─────────────────

@app.route("/")
def index():
    if "usuario" not in session:
        return redirect("/login")
    return render_template("index.html")


@app.route("/gerencia")
def gerencia():
    if "usuario" not in session:
        return redirect("/login")
    return render_template("gerencia.html")


# ───────────────── REGISTROS ─────────────────

@app.route("/api/registros/<tipo>")
def registros(tipo):
    periodo = request.args.get("periodo", periodo_actual())
    with get_db() as db:
        if tipo == "motos":
            rows = db.execute(
                "SELECT * FROM motos WHERE periodo=? ORDER BY id DESC",
                (periodo,)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM vehiculos WHERE periodo=? ORDER BY id DESC",
                (periodo,)
            ).fetchall()
    return jsonify([dict(r) for r in rows])


# ───────────────── REGISTRAR ─────────────────

@app.route("/api/registrar/<tipo>", methods=["POST"])
def registrar(tipo):
    data = request.json
    periodo = periodo_actual()
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    placa = data.get("placa","").strip().upper()
    with get_db() as db:
        if tipo == "motos":
            dup = db.execute(
                "SELECT id FROM motos WHERE placa=? AND periodo=?",
                (placa, periodo)
            ).fetchone()
            if dup:
                return jsonify({"ok": False, "error": f"La placa {placa} ya está registrada."})
            db.execute("""
            INSERT INTO motos
            (placa,chasis,cliente,cedula,fecha,observaciones,periodo,creado)
            VALUES (?,?,?,?,?,?,?,?)
            """,(
                placa,
                data.get("chasis",""),
                data.get("cliente",""),
                data.get("cedula",""),
                data.get("fecha",""),
                data.get("observaciones",""),
                periodo,
                ahora
            ))
        else:
            dup = db.execute(
                "SELECT id FROM vehiculos WHERE placa=? AND periodo=?",
                (placa, periodo)
            ).fetchone()
            if dup:
                return jsonify({"ok": False, "error": f"La placa {placa} ya está registrada."})
            db.execute("""
            INSERT INTO vehiculos
            (placa,chasis,cliente,cedula,fecha,motor,marca_modelo,observaciones,periodo,creado)
            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,(
                placa,
                data.get("chasis",""),
                data.get("cliente",""),
                data.get("cedula",""),
                data.get("fecha",""),
                data.get("motor",""),
                data.get("marca_modelo",""),
                data.get("observaciones",""),
                periodo,
                ahora
            ))
    return jsonify({"ok": True})


# ───────────────── ELIMINAR ─────────────────

@app.route("/api/eliminar/<tipo>/<int:rid>", methods=["DELETE"])
def eliminar(tipo, rid):
    tabla = "motos" if tipo == "motos" else "vehiculos"
    with get_db() as db:
        db.execute(f"DELETE FROM {tabla} WHERE id=?", (rid,))
    return jsonify({"ok": True})


# ───────────────── EXPORTAR EXCEL ─────────────────

@app.route("/api/exportar/<tipo>")
def exportar(tipo):
    periodo = request.args.get("periodo", periodo_actual())
    with get_db() as db:
        if tipo == "motos":
            rows = db.execute(
                "SELECT * FROM motos WHERE periodo=?",
                (periodo,)
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM vehiculos WHERE periodo=?",
                (periodo,)
            ).fetchall()
    if not rows:
        return jsonify({"error":"No hay datos"}),400
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = tipo
    if tipo == "motos":
        headers = ["ID","Placa","Chasis","Cliente","Cedula","Fecha","Observaciones","Registrado"]
        cols = ["id","placa","chasis","cliente","cedula","fecha","observaciones","creado"]
    else:
        headers = ["ID","Placa","Chasis","Cliente","Cedula","Fecha","Motor","Marca/Modelo","Observaciones","Registrado"]
        cols = ["id","placa","chasis","cliente","cedula","fecha","motor","marca_modelo","observaciones","creado"]
    ws.append(headers)
    for r in rows:
        ws.append([r[c] for c in cols])
    archivo = f"fanar_{tipo}_{periodo}.xlsx"
    ruta = os.path.join(EXPORTS, archivo)
    wb.save(ruta)
    return send_file(ruta, as_attachment=True, download_name=archivo)


# ───────────────── REINICIAR ─────────────────

@app.route("/api/reiniciar/<tipo>", methods=["POST"])
def reiniciar(tipo):
    periodo = periodo_actual()
    tabla = "motos" if tipo == "motos" else "vehiculos"
    with get_db() as db:
        rows = db.execute(
            f"SELECT * FROM {tabla} WHERE periodo=?",
            (periodo,)
        ).fetchall()
        datos = json.dumps([dict(r) for r in rows])
        db.execute("""
        INSERT INTO historial
        (periodo,tipo,datos,exportado)
        VALUES (?,?,?,?)
        """,(
            periodo,
            tipo,
            datos,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        db.execute(
            f"DELETE FROM {tabla} WHERE periodo=?",
            (periodo,)
        )
    return jsonify({"ok": True, "registros_guardados": len(rows)})


# ───────────────── PERIODOS ─────────────────

@app.route("/api/periodos")
def periodos():
    with get_db() as db:
        m = db.execute("SELECT DISTINCT periodo FROM motos").fetchall()
        v = db.execute("SELECT DISTINCT periodo FROM vehiculos").fetchall()
    todos = sorted(
        set([r["periodo"] for r in m] + [r["periodo"] for r in v]),
        reverse=True
    )
    return jsonify(todos or [periodo_actual()])


# ───────────────── STATS ─────────────────

@app.route("/api/stats")
def stats():
    periodo = periodo_actual()
    with get_db() as db:
        nm = db.execute(
            "SELECT COUNT(*) as c FROM motos WHERE periodo=?",
            (periodo,)
        ).fetchone()["c"]
        nv = db.execute(
            "SELECT COUNT(*) as c FROM vehiculos WHERE periodo=?",
            (periodo,)
        ).fetchone()["c"]
    return jsonify({"motos": nm, "vehiculos": nv, "periodo": periodo})


# ───────────────── RUN ─────────────────

if __name__ == "__main__":
    print("\nSistema FANAR iniciado")
    print("Abrir en navegador:")
    print("http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000)