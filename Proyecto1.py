import random
import numpy as np
from pysat.solvers import Minisat22

#Primero hay que ver cuantas n clausulas hay que recibir (cuantos array hay que recibir)

cantidadClausulas=int(input('Cantidad de clausulas: '))

#Luego hay que ver cuantas proposiciones hay

cantidadProposiciones=int(input('Cantidad de proposiciones: '))

#Hay que generar aleatoriedad

#negadorAleatorio recibe una proposicion x, y dependiendo del valor de la variable negar, la niega o la mantiene
def negadorAleatorio(x):
    negar=random.random() #negar es un numero aleatorio entre 0 y 1
    if negar>=0.5: #Si negar es mayor que 0.5
        return x #La proposición se mantiene
    else: #Si no
        return -x #Se niega

#generarListaAleatoria recibe la cantidad de clausulas y la cantidad de proposiciones y genera una lista al azar de formulas en 3-CNF
def generarListaAleatoria(clausulas,proposiciones):
    listaGenerada=np.zeros(clausulas,3) #Primero se crea una matriz de nx3 donde n es la cantidad de clausulas (o conjunciones)
    for i in range(0,clausulas): #Por cada clausula
        for j in range(0,3): #Para cada proposición dentro de una clausula
            proposicion=negadorAleatorio(random.randint(1,proposiciones)) #Elegir un literal al azar y al mismo tiempo negarlo aleatoriamente
            listaGenerada[i][j]=proposicion #Agregar el literal aleatorizado a la clausula i en el espacio j de la disyunción
    return listaGenerada
