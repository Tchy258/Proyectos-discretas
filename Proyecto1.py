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
    listaGenerada=np.zeros((clausulas,3)) #Primero se crea una matriz de nx3 con ceros donde n es la cantidad de clausulas (o conjunciones)
    for i in range(0,clausulas): #Por cada clausula
        literalesUtilizables=np.full(proposiciones,True)
        #Crear un registro de cuales literales son utilizables, True si es que lo son, False si es que no
        #A fin de ahorrar memoria, el indice 0 indica si el 1 es utilizable o no y así sucesivamente.
        for j in range(0,3): #Para cada proposición dentro de una clausula
            proposicion=random.randint(1,proposiciones) #Elegir un literal al azar
            while literalesUtilizables[proposicion-1]==False: #Si ya se usó dentro de esta clausula
                proposicion=random.randint(1,proposiciones) #Elegir otro al azar hasta que sea uno utilizable
            literalesUtilizables[proposicion-1]=False #Marcar el elegido como no utilizable dentro de esta clausula
            proposicion=negadorAleatorio(proposicion) #Aleatoriamente negar o mantener el literal
            listaGenerada[i][j]=proposicion #Agregar el literal aleatorizado a la clausula i en el espacio j de la disyunción
    return listaGenerada #Entrega la lista


#arbolDeVerdad es una clase que ordena las clausulas en forma de árbol binario, donde cada nodo tendrá un valor de 0 o 1 según
#los valores de verdad a utilizar para su clausula, luego todos los nodos deben tener valor 1 para satisfacer la formula 3-CNF
class arbolDeVerdad():
  def __init__(self,clausula,hijoIzq=None,hijoDer=None):
    self.clausula=clausula
    self.hijoIzq=hijoIzq
    self.hijoDer=hijoDer

#El método evaluar, dado un array de ceros y unos de tamaño 2^n donde n es la cantidad de literales, ve si la clausula actual
#es satisfactible revisando si es que al menos uno de los literales es cierto
  def evaluar(self,valoresDeVerdad):
    indiceLiteral1=int(abs(self.clausula[0]) -1) #Convertir los literales a valor absoluto y restar 1 para usarlos como indices
    indiceLiteral2=int(abs(self.clausula[1]) -1)
    indiceLiteral3=int(abs(self.clausula[2]) -1)
    indices=np.array([indiceLiteral1,indiceLiteral2,indiceLiteral3]) #Crear un arreglo con estos indices
    valuaciones=np.array([0,0,0]) #Crear un arreglo de tamaño 3 cuyos valores serán el resultado de evaluar cada literal (0 o 1)
    resultado=0 #Para ver si la clausula es satisfactible o no, 1 si es satisfactible, 0 si no, por defecto, no es satisfactible
    for i in range(0,3): #Para cada literal de la clausula
      if self.clausula[i]>0: #Si el literal no está negado
        if valoresDeVerdad[indices[i]]==1: #Y el valor de verdad es 1
          valuaciones[i]=1 #Entonces la valuación para este literal es 1 (True)
        else: #Si el valor de verdad es 0
          valuaciones[i]=0 #Entonces la valuación es 0 (False)
      elif self.clausula[i]<0: #Si el literal está negado
        if valoresDeVerdad[indices[i]]==0: #Y el valor de verdad es 0
          valuaciones[i]=1 #Entonces la valuación para este literal es 1 (True)
        else: #Si el valor de verdad es 1
          valuaciones[i]=0 #Entonces la valuación es 0 (False)
    resultado=max(valuaciones[0],valuaciones[1],valuaciones[2]) #Si al menos uno es cierto, el máximo será 1, si no, será 0
    return resultado

  #El método recorrer, dado un arreglo de valores de verdad, va evaluando cada clausula por separado recursivamente con el método evaluar y
  #retorna una 3 tupla donde el primer valor es un 0 o 1, usado para ver satisfactibilidad, el arreglo de valores de verdad para tener
  #una valuación testigo si es que se encuentra, y un tercer valor que puede ser None o una clausula no satisfecha si es que los valores
  #de verdad no satisfacen la fórmula para elegir nuevos valores de verdad que si satisfagan esa clausula.
  def recorrer(self,valoresDeVerdad):
    valor=self.evaluar(valoresDeVerdad) #Evaluar esta clausula para los valores de verdad dados
    if valor==1: #Si esta clausula se cumple
      if self.hijoIzq is None and self.hijoDer is None: #Si estoy en una hoja del árbol
        return (1,valoresDeVerdad,None) #Retornar 1 (True), la valuación testigo y None, porque todas las clausulas son satisfactibles en esta rama
      else: #Si no estoy en una hoja
        if self.hijoIzq is None and self.hijoDer is not None: #Si tengo hijo derecho pero no izquierdo
          return self.hijoDer.recorrer(valoresDeVerdad) #Retornar valuación del árbol del hijo derecho
        if self.hijoIzq is not None and self.hijoDer is None: #Si tengo hijo izquierdo pero no derecho
          return self.hijoIzq.recorrer(valoresDeVerdad) #Retornar valuación del árbol del hijo izquierdo
        else: #Si tengo ambos hijos
          izquierdo=self.hijoIzq.recorrer(valoresDeVerdad) #Evaluar el hijo izquierdo
          derecho=self.hijoDer.recorrer(valoresDeVerdad) #Evaluar el hijo derecho
          minimo=int(min(izquierdo[0],derecho[0])) #Ver el minimo entre los dos hijos, es decir, si al menos una clausula no se satisface, minimo es 0, si no, es 1
          clausula1=izquierdo[2] #Si el árbol izquierdo no es satisfactible, registrar la clausula a satisfacer, o un None si es que es satisfactible
          clausula2=derecho[2] #Lo mismo para el árbol derecho
          if clausula1 is None: #Si el árbol izquierdo es satisfactible
            return (minimo,valoresDeVerdad,clausula2) #Retornar el minimo, y la clausula no satisfactible del arbol derecho si es que no es satisfactible
          else: #Si el árbol derecho es satisfactible
            return (minimo,valoresDeVerdad,clausula1) #El caso análogo al de arriba
    else: #Si esta clausula no se cumple
      return (0,valoresDeVerdad,self.clausula) #Retornar 0 (False), los valores de verdad hasta el momento y la clausula insatisfactible
    
#construirArbol, dada una formula en 3-CNF en un array, construye un árbol binario balanceado a partir del arreglo con la lista de fórmulas
#separando la lista en intervalos de tamaño n_i/2 donde n_i es el tamaño del subintervalo.
#Inicialmente, limite inferior es 0 y limite superior es el tamaño de la lista menos 1
def construirArbol(lista,limiteInferior,limiteSuperior):
  if limiteInferior>limiteSuperior: #Caso base, estoy en un intervalo de clausulas vacio
    return None #Retornar None
  else: #Si estoy dentro de un rango de clausulas válido
    mitad=int((limiteInferior+limiteSuperior)//2) #Escoger la clausula (por su indice) que está en la mitad de este rango
    arbol=arbolDeVerdad(lista[mitad]) #Insertarla en el árbol binario
    arbol.hijoIzq=construirArbol(lista,limiteInferior,mitad-1) #En el hijo izquierdo, insertar el intervalo de clausulas a la izquierda
    arbol.hijoDer=construirArbol(lista,mitad+1,limiteSuperior) #En el hijo derecho, insertar el intervalo de clausulas a la derecha
    return arbol #Una vez todas las clausulas fueron insertadas (se llegó a intervalos vacios), retornar el árbol generado

#asignarValores, dado un arreglo de valores de verdad, literales de una clausula y un caso de una tabla de verdad para 3 literales,
#cambia los valores de verdad para dichos literales según el caso de la tabla de verdad, donde el caso 0 es [1,1,1] y el 7 [0,0,1]
#se omite el caso [0,0,0] ya que esos son los valores de verdad por defecto
def asignarValores(valoresDeVerdad,clausula,casoSubtabla):
  subtablaDeVerdad=np.array([[1,1,1],[1,1,0],[1,0,1],[1,0,0],[0,1,1],[0,1,0],[0,0,1]]) #Se genera la tabla de verdad
  indices=np.array([int(abs(clausula[0])-1),int(abs(clausula[1])-1),int(abs(clausula[2])-1)]) 
  #Se crea un arreglo que contiene los literales cuyos valores de verdad seran cambiados, en forma de indices para el arreglo valoresDeVerdad
  for i in range(0,3): #Por cada literal
    valoresDeVerdad[indices[i]]=subtablaDeVerdad[casoSubtabla][i] #Cambiar su valor de verdad según el caso de la tabla
  return valoresDeVerdad #Retornar los nuevos valores de verdad

  
#evaluarLista recibe una lista de literales en 3-CNF y dice si es satisfactible o no y si es que si, retorna una combinación que la satisface.
def evaluarLista(lista,cantidadClausulas,cantidadProposiciones):
  arbol=construirArbol(lista,0,cantidadClausulas-1) #Se construye el árbol binario para esta lista de conjunciones de literales en 3-CNF
  combinacionesTotales=int(2**cantidadProposiciones) #Siempre habrá 2^cantidad de literales combinaciones de verdad posibles
  valoresDeVerdad=np.full(cantidadProposiciones,0,dtype=int) #Crear un arreglo base para los valores de verdad, donde todos son False
  (esSatisfactible,valuacionTestigo,noSatisfecha)=arbol.recorrer(valoresDeVerdad)
  #Recorrer el árbol con los valores de verdad iniciales, ver si es satisfactible, si lo es,
  #dar una valuación testigo y si no, dar una clausula no satisfecha
  while esSatisfactible==0 and combinacionesTotales>0: #Mientras la formula no sea satisfactible con los valores de verdad actuales
    combinacionesDeClausula=0 #Crear un contador para probar cada combinación de valor de verdad para los literales de la clausula insatisfecha
    while esSatisfactible==0 and combinacionesDeClausula<7 and combinacionesTotales>0: #Mientras la formula no sea satisfactible y no haya probado todas las combinaciones actuales
      combinacionesTotales-=1 #Descontar una combinación posible del total
      valoresDeVerdad=asignarValores(valoresDeVerdad,noSatisfecha,combinacionesDeClausula) #Asignar nuevos valores de verdad para algun caso de la tabla de verdad
      combinacionesDeClausula+=1 #Avanzar el contador para el caso de la tabla
      (esSatisfactible,valuacionTestigo,noSatisfecha2)=arbol.recorrer(valoresDeVerdad) #Recorrer el árbol con los nuevos valores
      if noSatisfecha2 is not None: #Si aún hay una clausula insatisfecha
        if noSatisfecha2[0]==noSatisfecha[0] and noSatisfecha2[1]==noSatisfecha[1] and noSatisfecha2[2]==noSatisfecha[2]: #Ver si es la misma
          pass #Si es la misma, seguir y probar con otro caso de la tabla de verdad
        else: #Si es diferente
          noSatisfecha=noSatisfecha2 #Registrarla como la actual clausula no satisfecha
          break #Dejar de buscar valores de verdad para estos literales, pues ahora debo satisfacer una clausula distinta
  if esSatisfactible: #Si encontré una combinación de valores de verdad que satisface a todo el árbol
    return (True,valuacionTestigo) #Retornar True y la valuación testigo
  else: #Si agoté todas las combinaciones y no se pudo satisfacer el árbol
    return (False,None) #Retornar False y None
  
lista=generarListaAleatoria(cantidadClausulas,cantidadProposiciones)

(satisfactibilidad,valores)=evaluarLista(lista,cantidadClausulas,cantidadProposiciones)

print('Lista generada: ')
print(lista)
if not satisfactibilidad:
    print('No es satisfactible')
else:
    print('Es satisfactible')
    print('Valuacion testigo: ')
    print(valores)
