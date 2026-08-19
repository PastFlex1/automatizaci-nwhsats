import sqlite3
import datetime

DB_NAME = "crm_ventas.db"

def obtener_conexion():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_bd():
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Tabla Clientes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        perfil_fb TEXT,
        telefono TEXT,
        ciudad TEXT,
        interes TEXT,
        tipo_negocio TEXT,
        presupuesto TEXT,
        fecha_contacto TEXT,
        fecha_ultimo_contacto TEXT,
        estado TEXT DEFAULT 'Nuevo'
    )
    ''')

    # Tabla Catálogo
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS catalogo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        foto TEXT,
        medidas TEXT,
        precio REAL,
        caracteristicas TEXT,
        tiempo_fabricacion TEXT,
        activo INTEGER DEFAULT 1
    )
    ''')

    # Tabla Estadísticas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS estadisticas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT UNIQUE,
        publicaciones INTEGER DEFAULT 0,
        mensajes_recibidos INTEGER DEFAULT 0,
        clientes_interesados INTEGER DEFAULT 0,
        cotizaciones INTEGER DEFAULT 0,
        ventas_cerradas INTEGER DEFAULT 0
    )
    ''')

    # Tabla Interacciones
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interacciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        fecha TEXT,
        mensaje_cliente TEXT,
        respuesta_ia TEXT,
        FOREIGN KEY(cliente_id) REFERENCES clientes(id)
    )
    ''')

    conn.commit()
    conn.close()

# --- FUNCIONES DE CLIENTES ---

def registrar_o_actualizar_cliente(nombre, perfil_fb="", telefono="", ciudad="", interes="", tipo_negocio="", presupuesto="", estado="Nuevo"):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Buscar si existe por perfil_fb o nombre (si no hay perfil)
    if perfil_fb:
        cursor.execute("SELECT id FROM clientes WHERE perfil_fb = ?", (perfil_fb,))
    else:
        cursor.execute("SELECT id FROM clientes WHERE nombre = ?", (nombre,))
        
    resultado = cursor.fetchone()
    
    if resultado:
        cliente_id = resultado["id"]
        # Actualizar fecha y estado si cambió
        cursor.execute("""
            UPDATE clientes 
            SET fecha_ultimo_contacto = ?, estado = CASE WHEN estado != 'Venta cerrada' THEN ? ELSE estado END,
                interes = CASE WHEN ? != '' THEN ? ELSE interes END
            WHERE id = ?
        """, (fecha_actual, estado, interes, interes, cliente_id))
    else:
        cursor.execute("""
            INSERT INTO clientes (nombre, perfil_fb, telefono, ciudad, interes, tipo_negocio, presupuesto, fecha_contacto, fecha_ultimo_contacto, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nombre, perfil_fb, telefono, ciudad, interes, tipo_negocio, presupuesto, fecha_actual, fecha_actual, estado))
        cliente_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return cliente_id

def obtener_todos_los_clientes():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes ORDER BY fecha_ultimo_contacto DESC")
    clientes = cursor.fetchall()
    conn.close()
    return [dict(c) for c in clientes]

def actualizar_estado_cliente(cliente_id, nuevo_estado):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE clientes SET estado = ? WHERE id = ?", (nuevo_estado, cliente_id))
    conn.commit()
    conn.close()

def obtener_clientes_para_seguimiento(horas_inactividad=24):
    conn = obtener_conexion()
    cursor = conn.cursor()
    limite = (datetime.datetime.now() - datetime.timedelta(hours=horas_inactividad)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT * FROM clientes WHERE estado IN ('Interesado', 'Seguimiento') AND fecha_ultimo_contacto <= ?", (limite,))
    clientes = cursor.fetchall()
    conn.close()
    return [dict(c) for c in clientes]

# --- FUNCIONES DE ESTADÍSTICAS ---

def registrar_estadistica(campo, cantidad=1):
    conn = obtener_conexion()
    cursor = conn.cursor()
    fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
    
    cursor.execute("SELECT id FROM estadisticas WHERE fecha = ?", (fecha_hoy,))
    if cursor.fetchone():
        cursor.execute(f"UPDATE estadisticas SET {campo} = {campo} + ? WHERE fecha = ?", (cantidad, fecha_hoy))
    else:
        cursor.execute(f"INSERT INTO estadisticas (fecha, {campo}) VALUES (?, ?)", (fecha_hoy, cantidad))
        
    conn.commit()
    conn.close()

def obtener_estadisticas_mes():
    conn = obtener_conexion()
    cursor = conn.cursor()
    mes_actual = datetime.date.today().strftime("%Y-%m-")
    cursor.execute("SELECT SUM(publicaciones) as pub, SUM(mensajes_recibidos) as msg, SUM(clientes_interesados) as leads, SUM(cotizaciones) as cot, SUM(ventas_cerradas) as ventas FROM estadisticas WHERE fecha LIKE ?", (f"{mes_actual}%",))
    res = cursor.fetchone()
    conn.close()
    return dict(res) if res and res["pub"] is not None else {"pub": 0, "msg": 0, "leads": 0, "cot": 0, "ventas": 0}

# --- FUNCIONES DE CATÁLOGO ---

def agregar_producto_catalogo(nombre, foto, medidas, precio, caracteristicas, tiempo_fabricacion):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO catalogo (nombre, foto, medidas, precio, caracteristicas, tiempo_fabricacion)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, foto, medidas, precio, caracteristicas, tiempo_fabricacion))
    conn.commit()
    conn.close()

def obtener_catalogo():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catalogo WHERE activo = 1")
    productos = cursor.fetchall()
    conn.close()
    return [dict(p) for p in productos]

# Inicializar BD si es ejecutado directamente o importado por primera vez
inicializar_bd()
