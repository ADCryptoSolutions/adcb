#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
# Funcion que calcula el profit de una determinada
# estrategia dados w y la serie correspondiente al precio
import numpy as np

def profit(w,p):
  
  logReturn = np.log(p).diff().fillna(0)
  
  relativeReturn = np.exp(np.dot(w,logReturn)) - 1
  return relativeReturn

# convierte el 0.5 que aparece al principio de w al hacer
# (dif+1)/2 en los casos en los que se empieza con la orden wait
# en 0.0
def change5(f):
    if f == 0.5:
        return 0.0
    else:
        return f
