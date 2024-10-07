import sqlite3

# conectarse a la base de datos:
def conectar():
    try:
        conexion = sqlite3.connect('biblioteca.db')
        return conexion
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}.")
        return None

# crear las tablas de la base de datos:
def crear_tablas():
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            # tablas:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role_id INTEGER,
                    FOREIGN KEY (role_id) REFERENCES roles(id)
                )
            ''')
            # roles por defecto (usuario general y administrador):
            cursor.execute("INSERT OR IGNORE INTO roles (id, nombre) VALUES (1, 'Usuario General')")
            cursor.execute("INSERT OR IGNORE INTO roles (id, nombre) VALUES (2, 'Administrador')")
            conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al crear las tablas: {e}.")
        finally:
            conexion.close()

crear_tablas()
