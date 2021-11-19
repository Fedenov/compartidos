import matplotlib.pyplot as plt
#import matplotlib.animation as animacion
#from matplotlib import style
import csv
import time
#import turtle
import pandas as pd

class ControlPID (object):
    def __init__(self, SP, MIN_OUT, MAX_OUT, KP, KI, KD):
        self.SP = SP
        self.Min_acel = MIN_OUT
        self.Max_acel = MAX_OUT
        self.Kp = KP
        self.Ki = KI
        self.Kd = KD
        self.error = 0.0
        self.error_anterior = 0.0
        self.error_integral = 0.0
        self.error_derivativo = 0.0
    def controlar(self, PV, SP, T_MUESTREO):
        deltaT = T_MUESTREO
        self.error = PV - SP
        self.error_integral += self.error * deltaT
        self.error_derivativo = (self.error - self.error_anterior) / deltaT
        self.error_anterior = self.error
        aceleracion = self.Kp * self.error + self.Ki * self.error_integral + self.Kd * self.error_derivativo
        if aceleracion >= self.Max_acel:
            aceleracion = self.Max_acel
        if aceleracion <= self.Min_acel:
            aceleracion = self.Min_acel
        return [aceleracion, self.error, self.error_anterior, self.error_integral, self.error_derivativo]

class Transductor (object):
    def __init__(self, MIN_IN, MAX_IN, MIN_OUT, MAX_OUT):
        self.Min_in = MIN_IN
        self.Max_in = MAX_IN
        self.Min_out = MIN_OUT
        self.Max_out = MAX_OUT
    def Transducir (self, INPUT):
        derivada = (self.Max_out - self.Min_out) / (self.Max_in - self.Min_in)
        input_medio = (self.Max_in + self.Min_in) / 2
        out_medio = (self.Max_out + self.Min_out) / 2
        salida = (INPUT - input_medio) * derivada + out_medio
        return salida   


class Proceso(object):
    def __init__(self, VEL_OBJETIVO, VEL_INICIAL, DIST_INICIAL, CD, A_TRANSV, MASA, RHO, VEL_VIENTO):
        self.vel_obj = VEL_OBJETIVO
        self.vel_i = VEL_INICIAL
        self.dist_i = DIST_INICIAL
        self.Cd = CD
        self.A_transv = A_TRANSV
        self.masa = MASA
        self.rho = RHO
        self.vel_viento = VEL_VIENTO 
    def Procesar(self, acel, vel_viento, T_PROCESO):
        self.vel_viento = vel_viento
        deltaT = T_PROCESO
        vel_viento_rel = (acel * deltaT + self.vel_i) - self.vel_viento
        Arrastre = 0.5 * self.Cd * self.rho * self.A_transv * vel_viento_rel*vel_viento_rel
        acel_neta = acel - (Arrastre / self.masa)
        deltaX = 0.5 * acel_neta * (deltaT*deltaT) + self.vel_i * deltaT
        # print("Acel de arrastre", "{:.2f}".format(Arrastre/self.masa), "m/s2")
        # print("Vel viento", "{:.2f}".format(self.vel_viento), "m/s")
        # print("Acel*deltaT", "{:.2f}".format(acel*deltaT), "m/s2")
        # print("Vel viento rel", "{:.2f}".format(vel_viento_rel), "m/s")
        # print("DeltaT", "{:.2f}".format(deltaT), "s")
        # print("Vel inicial", "{:.2f}".format(self.vel_i), "m/s")
        # print("desplazamiento: ", "{:.2f}".format(deltaX), "m")
        distancia = self.dist_i - (deltaX - self.vel_obj * deltaT)
        self.dist_i = distancia
        self.vel_i = self.vel_i + acel_neta * deltaT
        return [distancia, acel_neta, deltaX, Arrastre]

class Computalizador (object):
    def __init__(self, nombre, C0, C1, C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15, C16, C17):
        self.nombre = nombre
        self.nombre_excel = nombre + ".csv"
        self.col0 = C0
        self.col1 = C1
        self.col2 = C2
        self.col3 = C3
        self.col4 = C4
        self.col5 = C5
        self.col6 = C6
        self.col7 = C7
        self.col8 = C8
        self.col9 = C9
        self.col10 = C10
        self.col11 = C11
        self.col12 = C12
        self.col13 = C13
        self.col14 = C14
        self.col15 = C15
        self.col16 = C16
        self.col17 = C17
        self.abscisas = []
        self.ordenadas1 = []
        self.ordenadas2 = []
        self.ordenadas3 = []
        self.ordenadas4 = []
        self.ordenadas5 = []
        self.ordenadas6 = []
        self.ordenadas7 = []
        self.ordenadas8 = []
        self.ordenadas9 = []
        self.ordenadas10 = []
        self.ordenadas11 = []
        self.ordenadas12 = []
        self.ordenadas13 = []
        self.ordenadas14 = []
        self.ordenadas15 = []
        self.ordenadas16 = []
        self.ordenadas17 = []
        # style.use('fivethirtyeight')
    def figura(self):
        fig = plt.figure()
        return fig
    def actualizar(self, t, acel, acel_net, min_acel, max_acel, dist, sp, err_int, err_der):
        self.abscisas.append(t)
        self.ordenadas2.append(acel)
        self.ordenadas13.append(max_acel)
        self.ordenadas14.append(min_acel)
        self.ordenadas6.append(sp)
        self.ordenadas11.append(dist)
        self.ordenadas15.append(err_int)
        self.ordenadas16.append(err_der)
        self.ordenadas12.append(acel_net)
    def plotear(self):
        fig, ((ax1, ax2),(ax3, ax4)) = plt.subplots(nrows = 2, ncols = 2, sharex = 'col')
        cero = []
        for i in range(len(self.abscisas)):
            cero.append(0)
        ax1.plot(self.abscisas, self.ordenadas2, color = 'b', label = self.col2)
        ax1.plot(self.abscisas, self.ordenadas12, color = 'c', label = self.col12)
        ax1.plot(self.abscisas, self.ordenadas13, color = 'k', linestyle = '--', label = self.col13)
        ax1.plot(self.abscisas, self.ordenadas14, color = 'k', linestyle = '--', label = self.col14)
        ax1.plot(self.abscisas, cero, color = 'k', linestyle = '--', linewidth = '1')
        ax1.legend(loc = 'lower right')
        ax1.set_title("Aceleracion motor y neta")
        ax1.set_ylabel('[m/s^2]')

        ax3.plot(self.abscisas, self.ordenadas11, color = 'r', label = self.col11)
        ax3.plot(self.abscisas, self.ordenadas6, color = 'g', label = self.col6)
        ax3.plot(self.abscisas, cero, color = 'k', linestyle = '--', linewidth = '1')
        ax3.invert_yaxis()
        ax3.legend(loc = 'lower right')
        ax3.set_title("Distancia al objetivo")
        ax3.set_xlabel(self.col0 + "[s]")
        ax3.set_ylabel('[m]')

        
        ax2.plot(self.abscisas, self.ordenadas15, color = 'm', label = self.col15)
        ax2.plot(self.abscisas, cero, color = 'k', linestyle = '--', linewidth = '1')
        ax2.legend(loc = 'lower right')
        ax2.set_title("Parametros PID")

        ax4.plot(self.abscisas, self.ordenadas16, color = 'g', label = self.col16)
        ax4.plot(self.abscisas, cero, color = 'k', linestyle = '--', linewidth = '1')
        ax4.legend(loc = 'lower right')      
        ax4.set_xlabel(self.col0 + "[s]")

        ax1.grid(linestyle = '--')
        ax2.grid(linestyle = '--')
        ax3.grid(linestyle = '--')
        ax4.grid(linestyle = '--')

        plt.tight_layout()
        nombrePNG = "Grafico de archivo " + self.nombre + ".png"
        plt.savefig(nombrePNG)
        plt.show()
    def exportar_png(self):
        plt.gcf()
        nombrePNG = "Grafico de " + self.nombre + ".png"
        plt.savefig(nombrePNG)
    def crear_archivo(self, c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c17):
        with open(self.nombre_excel, 'w', encoding='UTF8', newline='') as archivo:
            thewriter = csv.writer(archivo, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
            titulos = [c0, c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c17]
            thewriter = csv.DictWriter(archivo, fieldnames = titulos)
            thewriter.writeheader()
    def archivar(self, val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, val_8, val_9, val_10, val_17):
        lista = [val_0, val_1, val_2, val_3, val_4, val_5, val_6, val_7, val_8, val_9, val_10, val_17]
        with open(self.nombre_excel, 'a', newline='') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(lista)
            
                # titulos = [self.col0, self.col1, self.col2, self.col3, self.col4, self.col5, self.col6]
                # thewriter = writer(archivo, fieldnames = titulos)
                # thewriter.writeheader()
                # # thewriter.writerow({self.col0 : val_0, self.col1 : val_1, self.col2 : val_2, self.col3 : val_3, 
                # # self.col4 : val_4, self.col5 : val_5, self.col6 : val_6})
                # thewriter.writerow({self.col0 : val_0, self.col1 : val_1, self.col2 : val_2, self.col3 : val_3, 
                # self.col4 : val_4, self.col5 : val_5, self.col6 : val_6})


# class Ilustrador (object):
#     def __init__(self, dist_pantalla):
#         self.screen = turtle.Screen()
#         self.screen.setup(1280,900)
#         self.objetivo = turtle.Turtle()
#         self.objeto.shape('square')
#         self.objeto.color('blue')
#         self.objetivo.penup()
#         self.objetivo.left(180)
#         self.objetivo.goto(1200,200)
#         self.objetivo.color('blue')
#         self.objeto = turtle.Turtle()
#         self.objeto.shape('square')
#         self.objeto.color('black')
#         self.objeto.penup()
#         self.objeto.goto(SP-distancia, 200)
#         self.objeto.speed(0)
#     def Ilustrar(self, distancia):
#         pix_dist = distancia * 1280/dist_pantalla
#         self.objeto.goto(1200 - pixt_dist, 200)
