from os import write
import random
import numpy as np
from pysat.solvers import Minisat22
from stopwatch import StopWatch
#Primero hay que ver cuantas n clausulas hay que recibir (cuantos array hay que generar)

cantidadClausulas=int(input('Cantidad de clausulas: '))

#Luego hay que ver cuantas proposiciones (literales) hay

cantidadProposiciones=int(input('Cantidad de proposiciones: '))

#Hay que generar aleatoriedad

#negadorAleatorio recibe una proposicion x, y dependiendo del valor de la variable negar, la niega o la mantiene
def negadorAleatorio(x):
    negar=random.random() #negar es un numero aleatorio entre 0 y 1
    if negar>=0.5: #Si negar es mayor o igual que 0.5
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
    self.clausula=clausula #Variable para almacenar la clausula de este nodo
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
    resultado=int(max(valuaciones[0],valuaciones[1],valuaciones[2])) #Si al menos uno es cierto, el máximo será 1, si no, será 0
    return resultado



  #El método recorrer, dado un arreglo de valores de verdad, va evaluando cada clausula por separado recursivamente con el método evaluar y
  #retorna una 2 tupla donde el primer valor es un 0 o 1, usado para ver satisfactibilidad y el arreglo de valores de verdad para tener
  #una valuación testigo si es que se encuentra o en su defecto, un None.
  def recorrer(self,valoresDeVerdad):
    valor=self.evaluar(valoresDeVerdad) #Evaluar esta clausula para los valores de verdad dados
    if valor==1: #Si esta clausula se cumple
      if self.hijoIzq is None and self.hijoDer is None: #Si el nodo actual en una hoja del árbol
        return (1,valoresDeVerdad) #Retornar 1 (True), la valuación testigo y None, porque todas las clausulas son satisfactibles en esta rama
      else: #Si el nodo actual no es una hoja
        if self.hijoIzq is None and self.hijoDer is not None: #Si el nodo actual tiene hijo derecho pero no izquierdo
          return self.hijoDer.recorrer(valoresDeVerdad) #Retornar valuación del árbol del hijo derecho
        if self.hijoIzq is not None and self.hijoDer is None: #Si el nodo actual tiene hijo izquierdo pero no derecho
          return self.hijoIzq.recorrer(valoresDeVerdad) #Retornar valuación del árbol del hijo izquierdo
        else: #Si el nodo actual tiene ambos hijos
          izquierdo=self.hijoIzq.recorrer(valoresDeVerdad) #Evaluar el hijo izquierdo
          derecho=self.hijoDer.recorrer(valoresDeVerdad) #Evaluar el hijo derecho
          minimo=int(min(izquierdo[0],derecho[0])) #Ver el minimo entre los dos hijos, es decir, si al menos una clausula no se satisface, minimo es 0, si no, es 1
          return (minimo,valoresDeVerdad) #Retornar el minimo, y sus valores de verdad
    else: #Si esta clausula no se cumple
      return (0,valoresDeVerdad) #Retornar 0 (False), los valores de verdad hasta el momento y la clausula insatisfactible
    

  
#construirArbol, dada una formula en 3-CNF en un array, construye un árbol binario balanceado a partir del arreglo con la lista de fórmulas
#separando la lista en intervalos de tamaño n_i/2 donde n_i es el tamaño del subintervalo.
#Inicialmente, limite inferior es 0 y limite superior es el tamaño de la lista menos 1
def construirArbol(lista,limiteInferior,limiteSuperior):
  if limiteInferior>limiteSuperior: #Caso base, un intervalo de clausulas vacio
    return None #Retornar None
  else: #Si estoy dentro de un intervalo de clausulas válido
    mitad=int((limiteInferior+limiteSuperior)//2) #Escoger la clausula (por su indice) que está en la mitad de este intervalo
    arbol=arbolDeVerdad(lista[mitad]) #Insertarla en el árbol binario
    arbol.hijoIzq=construirArbol(lista,limiteInferior,mitad-1) #En el hijo izquierdo, insertar el intervalo de clausulas a la izquierda
    arbol.hijoDer=construirArbol(lista,mitad+1,limiteSuperior) #En el hijo derecho, insertar el intervalo de clausulas a la derecha
    return arbol #Una vez todas las clausulas fueron insertadas (se llegó a intervalos vacios), retornar el árbol generado

#asignarValores, toma un numero y lo convierte en binario para generar una posible fila de una tabla de verdad
#con "tamanoMaximo" cantidad de proposiciones
def asignarValores(caso,tamanoMaximo):
  binario=np.binary_repr(caso,width=tamanoMaximo) #Obtener la represntación binaria del número "caso" en forma de string
  arreglo=np.zeros(tamanoMaximo) #Crear un arreglo de ceros al cual copiar los datos del string generado
  for i in range(0,tamanoMaximo):
    arreglo[i]=int(binario[i]) #Copiar cada valor del string binario a un arreglo
  return arreglo #Retornar el arreglo


#evaluarLista recibe la lista de fórmulas en 3-CNF, la cantidad de clausulas y la cantidad de proposiciones y retorna la satisfactibilidad de la lista
#y una combinación de valores de verdad que satisface la lista, si es que hay alguna.
def evaluarLista(lista,cantidadClausulas,cantidadProposiciones):
  arbol=construirArbol(lista,0,cantidadClausulas-1) #Se construye el árbol binario para esta lista de conjunciones de literales en 3-CNF
  combinacionesTotales=int(2**cantidadProposiciones) #Siempre habrá 2^cantidad de literales combinaciones de verdad posibles
  valoresDeVerdad=np.full(cantidadProposiciones,0,dtype=int) #Crear un arreglo base para los valores de verdad, donde todos son False
  (esSatisfactible,valuacionTestigo)=arbol.recorrer(valoresDeVerdad)
  #Recorrer el árbol con los valores de verdad iniciales, ver si es satisfactible, si lo es,
  #dar una valuación testigo y si no, dar una clausula no satisfecha
  if esSatisfactible==0: #Si no es satisfactible para estos valores de verdad
    mitad=combinacionesTotales//2 #Dividir las posibles valuaciones en mitades
    izquierda=mitad #Desde mitad hacia atras
    derecha=mitad+1 #Desde mitad+1 hacia adelante
  while esSatisfactible==0 and combinacionesTotales>0 and izquierda>=0 and derecha<=2**cantidadProposiciones: 
    #Mientras la formula no sea satisfactible con los valores de verdad actuales y no se hayan agotado las posibilidades
    combinacionesTotales-=2 #Descontar dos combinaciones posibles del total
    valoresDeVerdad=asignarValores(izquierda,cantidadProposiciones) #Asignar nuevos valores de verdad para la conversion binaria del numero izquierda a valores de verdad
    (esSatisfactible,valuacionTestigo)=arbol.recorrer(valoresDeVerdad) #Recorrer el árbol con los nuevos valores
    if esSatisfactible: break #Si ahora es satisfactible, parar
    valoresDeVerdad=asignarValores(derecha,cantidadProposiciones) #Asignar nuevos valores de verdad con el numero derecha
    (esSatisfactible,valuacionTestigo)=arbol.recorrer(valoresDeVerdad) #Recorrer el árbol con los nuevos valores
    if esSatisfactible: break #Si es satisfactible, parar
    izquierda-=1 #Disminuir izquierda en 1
    derecha+=1 #Aumentar derecha en 1
  if esSatisfactible==1: #Si se encontró una combinación de valores de verdad que satisface a todo el árbol
    for i in range(0,cantidadProposiciones): #Convertir el arreglo binario a un arreglo con los literales correspondientes
        if valuacionTestigo[i]==1:
            valuacionTestigo[i]=i+1
        else:
            valuacionTestigo[i]=-1*(i+1)
    return (True,valuacionTestigo) #Retornar True y la valuación testigo
  else: #Si se agotaron todas las combinaciones y no se pudo satisfacer el árbol
    return (False,None) #Retornar False y None
      
    
cronometro=StopWatch() #Crear una instancia de stopwatch
tiempoTotal=0 #Variables para registrar el tiempo total de cada algoritmo
tiempoTotalMinisat=0

f = open('Resultados.txt', 'w') #f es un objeto para generar un archivo de texto en el que estarán todas las listas, su satisfactibilidad, testigo si es que hay y el tiempo total de cada algoritmo
for i in range(0,20): #A lo largo de 20 iteraciones
    print('Iteracion numero: '+str(i+1)) #Imprimir a la consola
    f.write('Iteracion numero: '+str(i+1)+'\n') #Escribir en el archivo
    lista=generarListaAleatoria(cantidadClausulas,cantidadProposiciones) #Se genera una lista
    cronometro.start() #Se empieza el cronometro
    (satisfactibilidad,valores)=evaluarLista(lista,cantidadClausulas,cantidadProposiciones) #Se evalua la lista
    tiempo=cronometro.stop() #Se detiene el cronometro
    tiempoTotal+=tiempo #Se añade el tiempo actual al tiempo total
    print('Lista generada: ')
    print(lista)
    for j in range(0,cantidadClausulas):
        f.write('[' + str(lista[j][0]) + ',' + str(lista[j][1]) +',' + str(lista[j][2]) +']\n')
    if not satisfactibilidad: #Si la lista no es satisfactible
        print('No es satisfactible')
        print('')
        f.write('No es satisfactible\n\n')
    else: #Si es satisfactible
        print('Es satisfactible')
        f.write('Es satisfactible\n')
        print('Valuacion testigo: ')
        f.write('Valuacion testigo: \n')
        print(valores) #Mostrar la valuacion testigo en la consola
        f.write('[') #Escribirla
        for j in range(0,valores.size):
            if j!=valores.size-1:
                f.write(str(valores[j])+',')
            else:
                f.write(str(valores[j])+']\n')
    print("Tiempo de ejecución: ",tiempo,'seg') #Mostrar el tiempo de ejecucion
    f.write('Tiempo de ejecución: '+str(tiempo)+' seg \n') #Escribirlo
    Lista=list(lista) #Se convierte el arreglo de arreglos numpy a una lista de listas de python para entregarlo como argumento al algoritmo minisat
    for i in range(0,cantidadClausulas): #Por cada arreglo en la nueva lista
        Lista[i]=list(Lista[i]) #Convertir el arreglo a lista python
        for j in range(0,3): #Por cada valor de la lista python
          Lista[i][j]=int(Lista[i][j]) #Convertir el valor a un entero
    cronometro.start() #Se empieza el cronometro
    with Minisat22(bootstrap_with=Lista) as m: #Se ejecuta el algoritmo minisat con la lista de clausulas 
        satisfactibilidadMinisat=m.solve() #Se guarda la satisfactibilidad según el algoritmo minisat (True o False)
        testigoMinisat=m.get_model() #Se rescata la valuacion testigo según el algoritmo minisat si es que existe
    tiempo=cronometro.stop() #Se guarda el tiempo transcurrido para ejectuar el algoritmo minisat
    tiempoTotalMinisat+=tiempo #Se añade al contador de su tiempo total
    print('Valuación Minisat22: '+str(satisfactibilidadMinisat)) #Se imprime la satisfactiblidad
    print('Testigo Minisat: ',testigoMinisat) #Se imprime la valuacion testigo
    f.write('Valuación Minisat22: '+str(satisfactibilidadMinisat)+'\n')
    f.write('Testigo Minisat:\n')
    if testigoMinisat is not None: #Si existe una valuacion testigo
      for i in range(0,len(testigoMinisat)): #Escribirla
        if i==0:
          f.write('[ ')
        if i!=len(testigoMinisat)-1:
          f.write(str(testigoMinisat[i])+' , ')
        else:
          f.write(str(testigoMinisat[i])+' ]\n')
    print('Tiempo de ejecución: ',tiempo,'s') #Imprimir el tiempo de ejecucion
    f.write('Tiempo de ejecución: '+str(tiempo)+' seg \n') #Escribirlo

print('')
print('Tiempo total de algoritmo propio: '+str(tiempoTotal)+' seg') #Imprimir el tiempo total del algoritmo programado
print('Tiempo promedio: '+str(tiempoTotal/20)+' seg') #Imprimir el tiempo promedio del algoritmo propio por cada iteracion
print('')
print('Tiempo total de algoritmo Minisat: '+str(tiempoTotalMinisat)+' seg') #Imprimir el tiempo total del algoritmo Minisat
print('Tiempo promedio: '+str(tiempoTotalMinisat/20)+'seg') #Imprimir el tiempo promedio del algoritmo Minisat por cada iteración
f.write('\nTiempo total de algoritmo propio: '+str(tiempoTotal)+'seg\n') #Escribir estos tiempos
f.write('Tiempo promedio: '+str(tiempoTotal/20)+' seg\n\n')
f.write('Tiempo total de algoritmo Minisat: '+str(tiempoTotalMinisat)+' seg\n')
f.write('Tiempo promedio: '+str(tiempoTotalMinisat/20)+' seg\n')
f.close() #Guardar el archivo
