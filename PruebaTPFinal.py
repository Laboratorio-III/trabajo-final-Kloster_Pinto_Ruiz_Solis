import hashlib
import datetime
import tkinter as tk
from tkinter import messagebox
import sqlite3
from fastapi import FastAPI
from typing import List

class Persona:
    def __init__(self, id, nombre, apellido, fecha_nacimiento, dni):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.fecha_nacimiento = fecha_nacimiento
        self.dni = dni

class Usuario(Persona):
    def __init__(self, id, nombre, apellido, fecha_nacimiento, dni, contraseña):
        super().__init__(id, nombre, apellido, fecha_nacimiento, dni)
        self.contraseña = self.encriptar_contraseña(contraseña)    #Encriptamos la contraseña del nuevo Usuario que creemos.
        self.ultimo_acceso = None

    def encriptar_contraseña(self, contraseña):
        # Utilizamos el algoritmo SHA256 para encriptar la contraseña que el usuario ingrese, y asi compararlas.
        sha256 = hashlib.sha256()
        sha256.update(contraseña.encode('utf-8'))
        return sha256.hexdigest()

    def verificar_contraseña(self, contraseña):
        # Verifica si la contraseña ingresada coincide con la contraseña almacenada encriptada
        encriptada = self.encriptar_contraseña(contraseña) #Aqui encriptamos la contraseña ingresada por el Usuario

        return encriptada == self.contraseña #Verificamos si esa Contraseña ingresada es igual a la ya guardada.

    def registrar_acceso(self):
        # Registra el tiempo del último acceso
        self.ultimo_acceso = datetime.datetime.now()
        print(f"Fecha de Ingreso: {self.ultimo_acceso}")
        

class Tarea:
    def __init__(self, id: int, titulo: str, descripcion: str, estado: str, fecha_creada: str, fecha_actualizada: str):
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.estado = estado
        self.fecha_creada = fecha_creada
        self.fecha_actualizada = fecha_actualizada

class AdminTarea:
    def __init__(self, db_nombre: str):    #La clase AdminTarea recibe a la base de datos "db_nombre" como parametro
        self.conn = sqlite3.connect(db_nombre)   #Creamos una conexion a la base de Datos "db_nombre" con Sqlite3, la conexion se guarda en self.conn

        self.cursor = self.conn.cursor() #se crea un objeto cursor que permite interactuar con la base de datos

        self._crear_tabla()  #Se crea la tabla si es que no existe con el metodo _crear_tabla



    def _crear_tabla(self):     #Aqui se crea una Tabla llamada "tareas" almacenada en la variable query 

        query = '''                          
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            estado TEXT,
            fecha_creada TEXT,
            fecha_actualizada TEXT
        )
        '''
        self.cursor.execute(query) # Aqui se ejecuta la "consulta SQL" almacenada en "query"
        self.conn.commit() #Aqui se confirman los cambios y se guardan de forma permanente en la base de Datos

    def agregar_tarea(self, tarea: Tarea) -> int:  #Esta clase recibe como parametro una variable tipo Tarea
        query = '''
        INSERT INTO tareas (titulo, descripcion, estado, fecha_creada, fecha_actualizada)
        VALUES (?, ?, ?, ?, ?)
        '''
        values = (tarea.titulo, tarea.descripcion, tarea.estado, tarea.fecha_creada, tarea.fecha_actualizada)
        self.cursor.execute(query, values)    #Los valores de la tarea en "value" se insertan en Tabla "tareas"
        self.conn.commit()                      #confirmando los cambios

        return self.cursor.lastrowid    #se devuelve el ID de la última fila insertada utilizando self.cursor.lastrowid


    def actualizar_estado_tarea(self, tarea_id: int, estado: str):
        query = '''
        UPDATE tareas SET estado = ?, fecha_actualizada = datetime('now') WHERE id = ?
        '''
        self.cursor.execute(query, (estado, tarea_id))
        self.conn.commit()

    def eliminar_tarea(self, tarea_id: int): #Funcion para eliminar una tarea usando como Parametro su ID, el cual es un entero.
        query = '''
        DELETE FROM tareas WHERE id = ?
        '''             #"query" eliminará la Tarea que cumpla la condicion "WHERE", es decir, la ID ingresada como parametro.

        self.cursor.execute(query, (tarea_id,)) #Se ejecuta la consulta query, eliminando la tarea con la ID ingresada.

        self.conn.commit()#Se confirman los cambios.

        
    def eliminar_todas_tareas(self):       #Funcion para eliminar todas las tareas
        #query contiene una "consulta" que al ejecutarse eliminará todo el contenido de la Tabla "tareas"
        query = '''
        DELETE FROM tareas          
        '''
        self.cursor.execute(query) #Aqui se ejecuta la "consulta" dentro de "query", que es eliminar los datos
        self.conn.commit()    #Se confirman los cambios.

        #Esta parte es para restablecer los numeros de "ID" al borrar todas las tareas, que empiece en 1 de nuevo
        query = '''
        DELETE FROM sqlite_sequence WHERE name='tareas'  
        '''                            
        self.cursor.execute(query) #Se ejecuta la nueva consulta
        self.conn.commit() # Se confirman los cambios.

    
    def traer_todas_tareas(self) -> List[Tarea]: #La funcion devuelve una Lista de objetos tipo "Tarea"
        query = '''
        SELECT * FROM tareas 
        '''                                #aqui "query" selecciona todas las columnas de la Tabla "tareas"
        self.cursor.execute(query)         #Ejecutamos la consulta "query"

        result = self.cursor.fetchall()    #Aqui simplemente se almacenan los datos de la consulta ejecutada anteriormente
        tareas = [Tarea(*row) for row in result]
        return tareas

# Crear una instancia de la ventana principal
root = tk.Tk()
root.title("Inicio de sesión")

def verificar_clave():
    nombre = nombre_entry.get()                 #"nombre" es igual a la entrada que ingresa el usuario en la interfaz informal
    clave = clave_entry.get()                   #lo mismo con la variable "clave"

    usuario = Usuario("1","Admin","Tesla","07/03/1989","44999380","12345") #Estos son los datos para ingresar.
    
    #Si el nombre y contraseña ingresados son igual al de "usuario" entonces se abrirá el Administrador_de_Tareas()
    if usuario.verificar_contraseña(clave) and nombre == usuario.nombre:
        usuario.registrar_acceso()
        messagebox.showinfo("Acceso permitido!", f"Bienvenido {usuario.nombre} {usuario.apellido}!\nDNI: {usuario.dni}\nNacimiento: {usuario.fecha_nacimiento}")
        
        root.destroy()                                               #root.destroy para desaparecer la ventana del Login
        Administrador_de_Tareas()         #Y se ejecuta la ventana "Administrador de Tareas"
    else:
        messagebox.showerror("Acceso denegado", "Nombre de usuario o clave incorrectos.")

# Crear un widget de etiqueta para el nombre
nombre_label = tk.Label(root, text="Nombre:")
nombre_label.grid(row=0, column=0, padx=10, pady=10)

# Crear un widget de entrada para el nombre
nombre_entry = tk.Entry(root)
nombre_entry.grid(row=0, column=1, padx=10, pady=10)

# Crear un widget de etiqueta para la clave
clave_label = tk.Label(root, text="Clave:")
clave_label.grid(row=1, column=0, padx=10, pady=10)

# Crear un widget de entrada para la clave (oculta)
clave_entry = tk.Entry(root, show="*")
clave_entry.grid(row=1, column=1, padx=10, pady=10)

# Crear un botón para verificar la clave
boton = tk.Button(root, text="Ingresar", command=verificar_clave)
boton.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

def Administrador_de_Tareas():
    root2 = tk.Tk()
    root2.title("Administrador de Tareas")
    admin_tareas = AdminTarea("tareas.db")
         
    #Funcion que utiliza el boton "Agregar Tarea" para ingresar una nueva tarea
    def agregar_tarea():
        # Los datos de entrada que ingresemos se guardan en las siguientes variables para crear esa nueva Tarea.
        titulo = tarea_entry.get()
        if not titulo:
            messagebox.showwarning("Error", "El ingresar un Nombre para la tarea es Obligatorio")
            return
        
        descripcion = descripcion_entry.get("1.0", tk.END).strip()  # Obtener el texto completo del widget de entrada de varias líneas
        estado = "Pendiente"
        fecha_creada = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fecha_actualizada = fecha_creada

        # Crear una instancia de la tarea
        tarea = Tarea(None, titulo, descripcion, estado, fecha_creada, fecha_actualizada)

        # Agregar la tarea a la base de datos
        admin_tareas.agregar_tarea(tarea)

        # Limpiar los widgets de entrada
        tarea_entry.delete(0, tk.END)
        descripcion_entry.delete("1.0", tk.END)


        # Actualizar la lista de tareas
        actualizar_lista_tareas()

        # Mostrar un mensaje de éxito
        messagebox.showinfo("Tarea agregada", "La tarea se agregó correctamente.")



    def actualizar_lista_tareas():
        # Limpiar la lista de tareas
        lista_tareas.delete(0, tk.END)

        # Obtener todas las tareas desde la base de datos
        tareas = admin_tareas.traer_todas_tareas()

        # Agregar las tareas a la lista
        for tarea in tareas:
            lista_tareas.insert(tk.END, f"ID: {tarea.id}, Título: {tarea.titulo}, Estado: {tarea.estado}, Fecha: {tarea.fecha_creada}, Descripcion: {tarea.descripcion}")


    
    

    def actualizar_estado():
        # Obtener la tarea seleccionada en la lista
        seleccion = lista_tareas.curselection()
        if len(seleccion) == 0:
            messagebox.showerror("Error", "Por favor, seleccione una tarea.")
            return

        # Metodo para obtener la ID de la tarea seleccionada
        tarea_id = int(lista_tareas.get(seleccion[0]).split(",")[0].split(":")[1].strip())

        # Obtener el nuevo estado de la tarea desde el usuario
        estado = estado_entry.get()

        # Actualizar el estado de la tarea en la base de datos
        admin_tareas.actualizar_estado_tarea(tarea_id, estado)

        # Actualizar la lista de tareass
        actualizar_lista_tareas()

        # Mostramos el mensaje
        messagebox.showinfo("Tarea actualizada", "El estado de la tarea se actualizó correctamente.")
    
    def eliminar_todas_tareas():
        admin_tareas.eliminar_todas_tareas()
        lista_tareas.delete(0, tk.END)
        messagebox.showinfo("Tareas eliminadas", "Todas las tareas se han eliminado correctamente.")


    def eliminar_tarea():
        # Obtener la tarea seleccionada en la lista
        seleccion = lista_tareas.curselection()
        if len(seleccion) == 0:
            messagebox.showerror("Error", "Por favor, seleccione una tarea.")
            return

        # Al seleccionar la tarea la dividimos en varias partes solo para obtener su ID.
        tarea_id = int(lista_tareas.get(seleccion[0]).split(",")[0].split(":")[1].strip())

        # Eliminar la tarea de la base de datos usando su ID.
        admin_tareas.eliminar_tarea(tarea_id)

        # Actualizar la lista de tareas
        actualizar_lista_tareas()

        # Mostrar un mensaje de éxito
        messagebox.showinfo("Tarea eliminada", "La tarea se eliminó correctamente.")



    # Crear un widget de etiqueta para la tarea
    tarea_label = tk.Label(root2, text="Tarea:")
    tarea_label.grid(row=3, column=0, padx=10, pady=10)

    # Crear un widget de entrada para la tarea
    tarea_entry = tk.Entry(root2)
    tarea_entry.grid(row=3, column=1, padx=10, pady=10)

    # Crear un widget de etiqueta para la descripción
    descripcion_label = tk.Label(root2, text="Descripción(opcional):")
    descripcion_label.grid(row=4, column=0, padx=10, pady=10)

    # Crear un widget de entrada de varias líneas para la descripción
    descripcion_entry = tk.Text(root2, height=5, width=30)
    descripcion_entry.grid(row=4, column=1, padx=10, pady=10)

    # Crear un botón para eliminar todas las tareas
    eliminar_todas_boton = tk.Button(root2, text="Eliminar todas las tareas", command=eliminar_todas_tareas)
    eliminar_todas_boton.grid(row=5, column=1, columnspan=3, padx=10, pady=10)

    # Crear un botón para agregar tarea
    agregar_boton = tk.Button(root2, text="Agregar tarea", command=agregar_tarea)
    agregar_boton.grid(row=5, column=0, padx=10, pady=10)

    # Crear un botón para ver las tareas
    ver_boton = tk.Button(root2, text="Ver tareas", command=actualizar_lista_tareas)
    ver_boton.grid(row=6, column=2, padx=10, pady=10)

    # Crear un widget de lista para mostrar las tareas
    lista_tareas = tk.Listbox(root2, width=50)
    lista_tareas.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    # Crear un widget de etiqueta para el estado
    estado_label = tk.Label(root2, text="Estado:")
    estado_label.grid(row=7, column=0, padx=10, pady=10)

    # Crear un widget de entrada para el estado
    estado_entry = tk.Entry(root2)
    estado_entry.grid(row=7, column=1, padx=10, pady=10)

    # Crear un botón para actualizar el estado de la tarea seleccionada
    actualizar_boton = tk.Button(root2, text="Actualizar estado", command=actualizar_estado)
    actualizar_boton.grid(row=8, column=0, padx=10, pady=10)

    # Crear un botón para eliminar la tarea seleccionada
    eliminar_boton = tk.Button(root2, text="Eliminar tarea", command=eliminar_tarea)
    eliminar_boton.grid(row=8, column=2, padx=10, pady=10)

    # Iniciar el bucle de eventos de la ventana secundaria
    root2.mainloop()

# Iniciar el bucle de eventos de la ventana principal
root.mainloop()


#Aqui comenzamos a usar FastAPI


app = FastAPI()         #Creamos la aplicacion

admin_tareas = AdminTarea("tareas.db") #admin_tareas ahora contiene los datos de la Base de datos.


#Ruta de FastAPI para que aparezcan todas las Tareas en la Web.
@app.get("/listar")
def ver_tareas():
    tareas = admin_tareas.traer_todas_tareas()        #"tareas" ahora contiene todas las tareas y sus datos.

    tarea_info = []             #en tareas_info se almacenaran todos los datos de cada tarea en forma de Diccionario.
    for tarea in tareas:
        tarea_info.append({
            "id": tarea.id,
            "titulo": tarea.titulo,
            "descripcion": tarea.descripcion,
            "estado": tarea.estado,
            "fecha_creada": tarea.fecha_creada,
            "fecha_actualizada": tarea.fecha_actualizada
        })
    return tarea_info    #Se devuelven todas las tareas dentro de tarea_info.


#Ruta de FastAPI para eliminar una Tarea con su ID.

@app.delete("/eliminar/{tarea_id}")     #Con la ruta /eliminar/ingresamos la ID de la tarea para eliminarla.
def eliminar_tarea(tarea_id: int): #El ID de la Tarea será un entero.
     
     if admin_tareas.eliminar_tarea(tarea_id):      #Si se pudo eliminar la tarea devuelve el siguiente mensaje.
        return f"La tarea con la ID: {tarea_id} fue eliminada con exito"
     else: #sino
        return "Tarea no encontrada en la base de datos."