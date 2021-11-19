import threading
import time
import matplotlib.animation as animacion
import matplotlib.pyplot as plt
import funciones_experimento as funciones
from itertools import count
import csv
from numpy import loadtxt

# RUN PROGRAM: CLTR + F5
# STOP PROGRAM: SHIFT + F5

# Variables de ejecucion de simulador
t_proceso = 1.0 #segundos
t_muestreo = 1.0 #segundos
t_ploteo = 1.0 #segundos
escalado_tiempo = 100.0 #factor se aumento de velocidad de la simulacion Xn veces la realidad
tipo_test = "e"
error_limite = 0.0 #minimo aceptable de error
duracion_test = 500 #segundos de duracion del simulacro. Cuando se pasa de ese tiempo, corta el simulacro
tiempo_cercania = 30.0 #tiempo en segundos que espera que se mantenga cerca de SP antes de finalizar la simulacion
#----------------------------------------
# Parametrizacion de fronteras de senales
MIN_ACEL = -3.0 #acleracion minima
MAX_ACEL = 3.0 #aceleracion maxima
MIN_VOLT = -5.0 #voltaje de salida minimo
MAX_VOLT = 5.0 #voltaje de salida maximo
#---------------------
# Configuracion de PID
Kp = 0.01
Ki = 0.0
Kd = 0.0
SP = 20.0 #distancia al objetivo en m
#-----------------------------------------------------------
# Variables base de construccion del entorno del experimento
VEL_OBJETIVO = 50.0 #km/h
VEL_INICIAL = 50.0 #km/h
DIST_INICIAL = 10.0 #m
CD = 0.29 #const
A_TRANSV = 2.0 #m2
MASA = 1450.0 #kg
RHO = 1.205 #densidad aire a PTN
VEL_VIENTO = -3.0 #km/h signo positivo es viento a favor. Negativo es viento en contra
#-------------------------------
# Variables de registro de datos
nombre_excel = "Datos Simulacro"
C0 = "Tiempo"
C1 = "Error"
C2 = "Aceleracion"
C3 = "Kp"
C4 = "Ki"
C5 = "Kd"
C6 = "SP"
C7 = "Distancia inicial"
C8 = "Vel objeto"
C9 = "Vel inicial"
C10 = "Vel viento"
C11 = "Distancia"
C12 = "Acel neta"
C13 = "Max acel"
C14 = "Min acel"
C15 = "Error integral"
C16 = "Error derivativo"
C17 = "Estado"
#------------------
#Variables internas
acel = 0.0
err = 0.0
dist = DIST_INICIAL
volt = 0.0
v_objetivo = 0.0
v_viento = 0.0
acel_neta = 0.0
deltaX = 0.0 #Desplazamiento por proceso
Farr = 0.0 #Fuerza de arrastre
#------------------

#CONVERTIR DE KM_H A M_S
VEL_OBJETIVO = VEL_OBJETIVO/3.6
VEL_INICIAL = VEL_INICIAL/3.6
VEL_VIENTO = VEL_VIENTO/3.6


P = funciones.Proceso(VEL_OBJETIVO, VEL_INICIAL, DIST_INICIAL, CD, A_TRANSV, MASA, RHO, VEL_VIENTO)
PID = funciones.ControlPID(SP, MIN_ACEL, MAX_ACEL, Kp, Ki, Kd)
Tr = funciones.Transductor(MIN_ACEL, MAX_ACEL, MIN_VOLT, MAX_VOLT)
Plt = funciones.Computalizador(nombre_excel, C0, C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15, C16, C17)
n_ciclos = count()

tiempo_arranque = time.time()
def transcurrido():
    t_transcurrido = (time.time() - tiempo_arranque) * escalado_tiempo
    return t_transcurrido

def ciclo_proceso(acel, t_ciclo):
    lista = P.Procesar(acel, VEL_VIENTO, t_ciclo)
    global dist
    global acel_neta
    global deltaX
    global Farr
    [dist, acel_neta, deltaX, Farr] = lista
    #time.sleep(t_ciclo)

def ciclo_PID(PV, t_ciclo):
    lista = PID.controlar(PV, SP, t_ciclo)
    global acel
    global err
    global err_ant
    global err_int
    global err_der
    acel = lista[0]
    err = lista[1]
    err_ant = lista[2]
    err_int = lista[3]
    err_der = lista[4]
    #print("Err anterior:", lista[2],"- Err int:", lista[3],"- Err deriv:", lista[4])
    volt = Tr.Transducir(acel)
    #time.sleep(t_ciclo)


terminar = False
# def ciclo_Plot(new0, new1, new21, new22, new3, SP, error, error_int, error_der, acel_net, val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, val_8, val_9, val_10, t_ploteo, opcion):
#     global terminar
#     if opcion == "a":
#         Plt.actualizar(new0, new1, new21, new22, new3, SP, error, error_int, error_der, acel_net)
#     elif opcion == "p":
#         Plt.plotear()
#     Plt.archivar(val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, val_8, val_9, val_10)
#     # time.sleep(t_ploteo)


Plt.crear_archivo(C0, C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C17)


def main():
    # aca va toda la linea de logica del simulacro
    tiempos_crono = []
    setpoints_crono = []
    vientos_crono = []
    global cambios
    global paso_crono
    paso = count()
    paso_crono = next(paso)
    try:
        with open('Cronologia_SP.csv', 'r') as sp_crono:
            lector = csv.reader(sp_crono)
            next(lector)
            for filas in lector:
                filas = filas[0].split(sep =";")
                tiempos_crono.append(filas[0])
                setpoints_crono.append(filas[1])
                vientos_crono.append(filas[2])
            print("Se encontro un cronograma")
        cambios = len(tiempos_crono)
    except:
        print("No se encontro un cronograma")
        cambios = 1
    
    ciclos = next(n_ciclos)
    t_ciclos_base = min(t_proceso, t_muestreo, t_ploteo)
    ciclos_proceso = t_proceso / t_ciclos_base
    ciclos_muestreo = t_muestreo / t_ciclos_base
    ciclos_ploteo = t_ploteo / t_ciclos_base
    t_ciclo_base_escalado = t_ciclos_base / escalado_tiempo
    aproximado = 0.0
    terminar = False
    estado = ""
    tiempo = transcurrido()

    while terminar == False and tiempo < duracion_test:
        global SP
        global VEL_VIENTO
        if paso_crono < len(setpoints_crono):
            f = float(tiempos_crono[paso_crono])
            if tiempo > f:
                SP = float(setpoints_crono[paso_crono])
                VEL_VIENTO = float(vientos_crono[paso_crono])
                paso_crono = next(paso)
        
        ciclos = next(n_ciclos)
        print("LAP", ciclos)
        print("tiempo: ", "{:.1f}".format(transcurrido()), "s")
        if ciclos % ciclos_proceso == 0:
            ciclo_proceso(acel, t_proceso)
        if ciclos % ciclos_muestreo == 0:
            ciclo_PID(dist, t_muestreo)
        if ciclos % ciclos_ploteo == 0:
            tiempo = transcurrido()
            Plt.actualizar(tiempo, acel, acel_neta, MIN_ACEL, MAX_ACEL, dist, SP, err_int, err_der)
            Plt.archivar(tiempo, err, acel, Kp, Ki, Kd, SP, DIST_INICIAL, VEL_OBJETIVO, VEL_INICIAL, VEL_VIENTO, estado)
            #ciclo_Plot(tiempo, acel, MAX_ACEL, MIN_ACEL, dist, SP, err, err_int, err_der, acel_neta, tiempo, , val_2, val_3, val_4, val_5, val_6, t_ploteo, "a")
        
        if abs(err) < error_limite and aproximado == 0.0:
            aproximado = transcurrido()
            #print("aproximado", aproximado)
            estado = "Proximo"
        elif abs(err) < error_limite and aproximado > 0.0:
            dT = transcurrido()
            #print("tiempo en rango aceptable: ", dT, "s")
            dT = dT - aproximado
            #print("dT", dT)
            estado = "Proximo"
            if dT > tiempo_cercania:
                terminar = True
                print("> OBJETIVO ALCANZADO <")
                estado = "EXITOSO"
        elif abs(err) > error_limite and aproximado > 0.0:
            aproximado = 0.0
            estado = ""
        elif err + SP <= 0:
            print(">> CRASH !!! <<")
            estado = "CRASH"
            #terminar = True

        time.sleep(t_ciclo_base_escalado)
        print("------------------")
    Plt.plotear()
    #ciclo_Plot(tiempo, acel, MAX_ACEL, MIN_ACEL, dist, SP, tiempo, acel, err, dist, SP, VEL_OBJETIVO, VEL_VIENTO, t_ploteo, "p")
    #Plt.exportar_png()
            

if __name__ == '__main__':
    main()