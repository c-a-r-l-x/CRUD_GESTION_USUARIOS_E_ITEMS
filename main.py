import sqlite3
import re
import bcrypt

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

def validar_username(username):
    return len(username) >= 5 and len(username) <= 20

def validar_password(password):
    return len(password) >= 8 and re.search(r"[A-Za-z]", password) and re.search(r"[0-9]", password)

def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def encriptar_contraseña(contraseña):
    salt = bcrypt.gensalt()
    contraseña_encriptada = bcrypt.hashpw(contraseña.encode('utf-8'), salt)
    return contraseña_encriptada

def registrar_usuario():
    conexion = conectar()
    if conexion:
        try:
            username = input("Ingrese su nombre de usuario (5-20 caracteres): ")
            if not validar_username(username):
                print("El nombre de usuario debe tener entre 5 y 20 caracteres.")
                return
            
            password = input("Ingrese su contraseña (mínimo 8 caracteres, con letras y números): ")
            if not validar_password(password):
                print("La contraseña debe tener al menos 8 caracteres, con al menos una letra y un número.")
                return

            email = input("Ingrese su email: ")
            if not validar_email(email):
                print("El formato del email no es válido.")
                return
            
            # encriptar la contraseña:
            password_encriptada = encriptar_contraseña(password)

            # asignar el rol:
            rol = input("Seleccione el rol (1 para Usuario General, 2 para Administrador): ")
            if rol == '1':
                rol_id = 1
            elif rol == '2':
                rol_id = 2
            else:
                print("Opción de rol no válida. Solo se permite 1 (Usuario General) o 2 (Administrador).")
                return

            cursor = conexion.cursor()
            cursor.execute("INSERT INTO usuarios (username, password, email, role_id) VALUES (?, ?, ?, ?)", 
                           (username, password_encriptada, email, rol_id))
            conexion.commit()
            print("Usuario registrado con éxito.")
        except sqlite3.IntegrityError:
            print("El nombre de usuario o email ya está en uso.")
        except sqlite3.Error as e:
            print(f"Error al registrar usuario: {e}.")
        finally:
            conexion.close()

def verificar_contraseña(contraseña, hash_contraseña):
    return bcrypt.checkpw(contraseña.encode('utf-8'), hash_contraseña)

def iniciar_sesion():
    conexion = conectar()
    if conexion:
        try:
            username = input("Ingrese su nombre de usuario: ")
            password = input("Ingrese su contraseña: ")

            cursor = conexion.cursor()
            cursor.execute("SELECT password, role_id FROM usuarios WHERE username = ?", (username,))
            usuario = cursor.fetchone()

            if usuario:
                contraseña_encriptada, role_id = usuario
                if verificar_contraseña(password, contraseña_encriptada):
                    print("Inicio de sesión exitoso.")
                    return role_id
                else:
                    print("Contraseña incorrecta.")
            else:
                print("Usuario no encontrado.")
            return None
        except sqlite3.Error as e:
            print(f"Error al iniciar sesión: {e}.")
            return None
        finally:
            conexion.close()

def listar_usuarios():
    conexion = conectar()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT username, email, role_id FROM usuarios")
            usuarios = cursor.fetchall()

            if usuarios:
                print("\n--- Lista de Usuarios ---")
                for usuario in usuarios:
                    print(f"- Username: {usuario[0]} | Email: {usuario[1]} | Role ID: {usuario[2]}.")
            else:
                print("No hay usuarios registrados.")
        except sqlite3.Error as e:
            print(f"Error al listar usuarios: {e}.")
        finally:
            conexion.close()

crear_tablas()
registrar_usuario()
iniciar_sesion()
listar_usuarios()
