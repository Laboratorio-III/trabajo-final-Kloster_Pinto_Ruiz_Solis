from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from Interfaz import AdminTarea

app = FastAPI()
admin_tarea = AdminTarea("tareas.db")

# Crear una instancia de HTTPBasic para manejar la autenticación básica HTTP
security = HTTPBasic()               

# Función para verificar las credenciales del usuario
def verificar_credenciales(credenciales: HTTPBasicCredentials = Depends(security)):  
    usuario = "Admin"                                      #Se ejecuta security y la funcion, si los datos son
    contraseña = "12345"                                   #correctos la funcion devuelve True
    if credenciales.username == usuario and credenciales.password == contraseña:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Los datos ingresados son incorrectos",
        )

@app.delete("/eliminar/{tarea_id}")   #Si la funcion devuelve True se ejecutaran las rutas solicitadas por el Usuario.
async def eliminar_tarea(tarea_id: int, autorizado: bool = Depends(verificar_credenciales)):
    if admin_tarea.eliminar_tarea(tarea_id):
        return {"mensaje": "Tarea eliminada correctamente"}
    else:
        return {"mensaje": "La tarea que intentas eliminar no existe"}
    
@app.delete("/borrar")
async def borrar_todo(autorizado: bool = Depends(verificar_credenciales)):
    if admin_tarea.eliminar_todas_tareas():
        return {"mensaje": "Tareas borradas correctamente"}
    else:
        return {"mensaje": "No hay tareas para borrar"}
    

@app.get("/tarea/{tarea_id}")
async def obtener_tarea(tarea_id: int, autorizado : bool = Depends(verificar_credenciales)):
    Tarea = admin_tarea.obtener_tarea(tarea_id)
    if Tarea:
        return Tarea
    else:
        return {"error": "No se pudo encontrar la tarea"}
