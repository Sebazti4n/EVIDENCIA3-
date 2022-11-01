

from ast import While
import datetime
import math
from pickle import TRUE
from queue import Empty
import sqlite3
import sys
import uuid
import os
import xlsxwriter

client = ''

iterations = 15

iterationsTxt = 3

"""
Creamos el modelo de base de datos si no existe un archivo de sql lite e imprimimos el inicio de estado de la base de datos

"""
if not os.path.exists('db.sqlite3'):
    print("\t"*iterations + "[+ Generando Database +]\n")
    db = sqlite3.connect('db.sqlite3')
    
    """
    Creacion de tabla Clientes

    """
    db.cursor().execute('''
        CREATE TABLE IF NOT EXISTS Clientes(
            id TEXT PRIMARY KEY,
            nombre TEXT
        )
    ''')

    """
    Creacion de tabla Salas

    """
    db.cursor().execute('''
        CREATE TABLE IF NOT EXISTS Salas(
            id TEXT PRIMARY KEY,
            nombre TEXT,
            ocupacion INTEGER,
            turno TEXT
        )
    ''')

    """
    Creacion de tabla Reservaciones

    """
    db.cursor().execute('''
        CREATE TABLE IF NOT EXISTS Reservaciones(
            id TEXT PRIMARY KEY,
            nombre TEXT,
            fecha TEXT,
            sala_id TEXT,
            turno_id TEXT,
            cliente_id TEXT
        )
    ''')
    db.commit()
else:
    """
    Reutilizamos el modelo de base de datos si ya existe un archivo de sql lite e imprimimos el estado de la base de datos

    """
    db = sqlite3.connect('db.sqlite3')
    print("\t"*iterationsTxt + "[+ Reutilizando Database +]\n")

"""
Imprimimos en pantalla el menu principal

"""
def menuPrincipal():
    print("****************************************************************************************************************")
    print("*" + f"{'Menu Principal' : >50}" + f"{'*' : >61}")
    print("****************************************************************************************************************")
    print(f"{'1.- Salir' : <50}")
    print(f"{'2.- Registrar Cliente' : <50}")
    print(f"{'3.- Registrar Sala' : <50}")
    print(f"{'4.- Reportes' : <50}")
    print(f"{'5.- Reservaciones' : <50}")
    return input("\t"*iterationsTxt + '[+ seleccione una opcion valida del menu +]:\n')


"""
Imprimimos en pantalla el menu reportes

"""
def menuReportes():
    print("****************************************************************************************************************")
    print("*" + f"{'Reportes' : >50}" + f"{'*' : >61}")
    print("****************************************************************************************************************")
    print(f"{'1.- Salir' : <50}")
    print(f"{'2.- Reporte Excel' : <50}")
    print(f"{'3.- Reporte Pantalla' : <50}")
    return input("\t"*iterationsTxt + '[+ seleccione una opcion valida del menu +]:\n')


"""
Imprimimos en pantalla el menu reservaciones

"""
def menuReservaciones():
    print("****************************************************************************************************************")
    print("*" + f"{'Reservaciones' : >50}" + f"{'*' : >61}")
    print("****************************************************************************************************************")  
    print(f"{'1.- Salir' : <50}")
    print(f"{'2.- Eliminar Reservacion' : <50}")
    print(f"{'3.- Consultar Disponibilidad' : <50}")
    print(f"{'4.- Modificar Reservacion' : <50}")
    print(f"{'5.- Nueva Reservacion' : <50}")
    return input("\t"*iterationsTxt + '[+ seleccione una opcion valida del menu +]:\n')


"""
Funcion para agregar un cliente a la db

"""
def agregarCliente(nombre):
    id = generarId()
    db.cursor().execute('''INSERT INTO Clientes(id,nombre)
                  VALUES(?,?)''', (id, nombre))
    db.commit()
    return id


"""
Funcion para agregar una sala a la db

"""
def agregarSala(nombre, ocupacion):
    for turno in ['Matutino', 'Vespertino', 'Nocturno']:
        id = generarId()
        db.cursor().execute('''INSERT INTO Salas(id,nombre,ocupacion,turno)
                        VALUES(?,?,?,?)''', (id, nombre, ocupacion, turno))
    db.commit()

"""
Funcion para agregar una reservacion a la db

"""
def agregarReservacion(nombre, fecha, sala, client):
    id = generarId()
    db.cursor().execute('''INSERT INTO Reservaciones(id,nombre,fecha,sala_id,cliente_id)
                  VALUES(?,?,?,?,?)''', (id, nombre, fecha, sala, client))
    db.commit()

    print("****************************************************************************************************************")
    print("*" + f"{'Reserva con Folio [{folio}]' : >50} Generada".format(folio=id) + f"{'*' : >52}")
    print("****************************************************************************************************************")     
    

"""
Funcion para editar una reservacion

"""
def editarReservacion(folio, nombre):
    db.cursor().execute('''UPDATE Reservaciones SET nombre = ? WHERE id = ?''', (nombre, folio))
    db.commit()


"""
Funcion para eliminar una reservacion

"""
def eliminarReservacion(folio):
    today = datetime.datetime.now()
    eventDay = db.cursor().execute('''SELECT fecha FROM Reservaciones Where id = ? ''', (folio,)).fetchone()
    if eventDay:
        delta = convertirFecha(eventDay[0]) - today
        print(delta.days)
        if(delta.days >= 3):
            opcion = input("\t"*iterationsTxt + "[+ ¿Desea Borrar la Reservacion? Y/N +]")
            if opcion == 'Y' or opcion == 'y':
                db.cursor().execute('''Delete FROM Reservaciones WHERE id = ?''', (folio,))
                db.commit()
            if opcion == 'N' or opcion == 'n':
                return
        else:
            print("\t"*iterationsTxt + "[+ Es Necesario 3 Dias Anticipacion para Eliminar Reservacion +]")
    
    
"""
Funcion para mostrar salas disponibles dada una fecha en especifico

"""
def mostrarSalasDisp(fecha):
    print("****************************************************************************************************************")
    print("*" + f"{'Salas Disponibles {fecha}' : >50}".format(fecha=fecha) + f"{'*' : >58}")
    print("****************************************************************************************************************")     
    salas = db.cursor().execute(
        "SELECT id, nombre, turno FROM salas WHERE id NOT IN(SELECT sala_id FROM Reservaciones) ").fetchall()
    print(f"{'Sala' : <40}{'Nombre' : <40}{'Turno' : <40}")
    for sala in salas:
        print(f"{sala[0] : <40}{sala[1] : <40}{sala[2] : <40}")
    print("\n\n")

"""
Funcion para mostrar reservaciones dada una fecha en especifico

"""
def obtenerReporteReservacion(fecha):
    print("****************************************************************************************************************")
    print("*" + f"{'Reservaciones {fecha}' : >50}".format(fecha=fecha) + f"{'*' : >58}")
    print("****************************************************************************************************************")
    print(f"{'Folio' : <35}{'Cliente' : <35}{'Evento' : <35}{'Turno' : <35}")
    eventos = db.cursor().execute('''SELECT sala.nombre, client.nombre, reser.nombre, sala.turno from Reservaciones reser join Salas sala on reser.sala_id = sala.id join Clientes client on client.id = reser.cliente_id where reser.fecha = ?''', (fecha,)).fetchall()
    for evento in eventos:
        print(f"{evento[0] : <35}{evento[1] : <35}{evento[2] : <35}{evento[3] : <35}")
    print("\n\n")

"""
Funcion para mostrar reservaciones 

"""
def obtenerListaReservacion():
    print("****************************************************************************************************************")
    print("*" + f"{'Reservaciones' : >50}" + f"{'*' : >61}")
    print("****************************************************************************************************************")
    print(f"{'Folio' : <35}{'Cliente' : <35}{'Evento' : <35}{'Turno' : <35}")
    eventos = db.cursor().execute('''SELECT reser.id, client.nombre, reser.nombre, sala.turno from Reservaciones reser join Salas sala on reser.sala_id = sala.id join Clientes client on client.id = reser.cliente_id''').fetchall()
    for evento in eventos:
         print(f"{evento[0] : <35}{evento[1] : <35}{evento[2] : <35}{evento[3] : <35}")
    print("\n\n")

"""
Funcion para exportar reservaciones dada una fecha en especifico a xlsx

"""
def exportarReporteReservacion(fecha):
    eventos = db.cursor().execute('''SELECT sala.nombre, client.nombre, reser.nombre, sala.turno from Reservaciones reser join Salas sala on reser.sala_id = sala.id join Clientes client on client.id = reser.cliente_id where reser.fecha = ?''', (fecha,)).fetchall()
    workbook = xlsxwriter.Workbook('reservaciones.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write( 0, 0, 'Folio')
    worksheet.write( 0, 1, 'Cliente')
    worksheet.write( 0, 2, 'Evento')
    worksheet.write( 0, 3, 'Turno')
    for i, row in enumerate(eventos):
        for j, value in enumerate(row):
            worksheet.write( i + 1, j, value)
    workbook.close()
    
"""
Funcion para convertir una fecha desde entrada de texto

"""    
def convertirFecha(fecha):
    return datetime.datetime.strptime(fecha, '%d/%m/%Y')

"""
Funcion para obtener una fecha desde entrada de texto

"""
def obtenerFecha():
    fecha = ''
    while not (validarFecha(fecha)):
        fecha = input("Ingrese Una Fecha Valida en Formato dd/mm/yyyy:\n")
    return fecha

"""
Funcion para validar el formato correcto de una fecha 

"""
def validarFecha(fecha):
    val = False
    try:
        datetime.datetime.strptime(fecha, '%d/%m/%Y')
        val = True
    except ValueError:
        val = False
    return val

"""
Funcion para generar un id aleatorio

"""
def generarId():
    return str(uuid.uuid1()).split('-')[0]

"""
Funcion para limpiar la consola

"""
def limpiarConsola():
    os.system('cls' if os.name == 'nt' else 'clear')

"""
Funcion para salir del programa

"""
def salir():
    opcion = input("\t"*iterationsTxt + "[+ ¿Desea Borrar la DB? Y/N +]")
    if opcion == 'Y' or opcion == 'y':
        db.close()
        os.remove("db.sqlite3")
        sys.exit()
    if opcion == 'N' or opcion == 'n':
        db.close()
        sys.exit()

"""
Funcion para simular un enter

"""
def enter():
    text = 'jkljkl'
    while text:
        text = input("\t"*iterationsTxt + "[+ Press Enter to Continue +]")
        limpiarConsola()

"""
Punto de inicio del programa

"""
while True:
    #limpiarConsola()
    if client:
        option = menuPrincipal()
        option2 = ''
        if int(option) == 1:
            salir()
        if int(option) == 2:
            nombre = input('Ingresa Nombre:\n')
            client = agregarCliente(nombre)
            enter()
        if int(option) == 3:
            nombre = input('Ingresa Nombre:\n')
            ocupacion = input('Ingresa Ocupacion Sala:\n')
            agregarSala(nombre, ocupacion)
            enter()
        if int(option) == 4:
            option2 = menuReportes()
            if int(option2) == 1:
                print("")
            if int(option2) == 2:
                fecha = obtenerFecha()
                exportarReporteReservacion(fecha)
                enter()
            if int(option2) == 3:
                fecha = obtenerFecha()
                obtenerReporteReservacion(fecha)
                enter()
        if int(option) == 5:
            option2 = menuReservaciones()
            if int(option2) == 1:
                print("")
            if int(option2) == 2:
                obtenerListaReservacion()
                folio = input('Ingresa Folio a Eliminar:\n')
                eliminarReservacion(folio)
                enter()
            if int(option2) == 3:
                fecha = obtenerFecha()
                mostrarSalasDisp(fecha)
                enter()
            if int(option2) == 4:
                obtenerListaReservacion()
                folio = input('Ingresa Folio a Modificar:\n')
                nombre = input('Ingresa Nombre:\n')
                editarReservacion(folio, nombre)
                enter()
            if int(option2) == 5:
                nombre = input('Ingresa Nombre Reservacion:\n')
                fecha = obtenerFecha()
                eventDay = convertirFecha(fecha)
                today = datetime.datetime.now()
                delta = eventDay - today
                if(delta.days >= 2):
                    mostrarSalasDisp(fecha)
                    sala = input('Ingresa Folio Sala a Reservar:\n')
                    agregarReservacion(nombre, fecha, sala, client)
                    enter()
                else:
                    print("\t"*iterationsTxt + "[+ Es Necesario 2 Dias Anticipacion para Agregar Reservacion +]")
                    enter()
    else:
        print("\t"*iterationsTxt +
              '[+ Es Necesario Registrarse o Ingrese Folio de Usuario +]')
        clientes = db.cursor().execute('''select id, nombre from clientes''').fetchall()
        print("****************************************************************************************************************")
        print("*" + f"{'Clientes' : >50}" + f"{'*' : >61}")
        print("****************************************************************************************************************")
        print(f"{'Folio' : <35}{'Nombre' : <35}")
        for cliente in clientes:
            print(f"{cliente[0] : <35}{cliente[1] : <35}")
        nombre = input("\t"*iterationsTxt +
                       '[+ Ingrese Nuevo Nombre Cliente o Folio Cliente +]:\n')
        found = False
        for cliente in clientes:
            if nombre == cliente[0]:
                found = True
        if found:
            client = nombre
        else:
            client = agregarCliente(nombre)
            enter()


