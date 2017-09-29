#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
import pandas as pd
from peakdetect import peakdetect
import pylab as plt

def ml_data(w):
	
	# separando fechas de precios
	y = w.values
	x = w.index.values
	
	# encontrando maximos y minimos locales.
	# peakdetect devuelve una lista con numpy arrays 1x2
	_max, _min = peakdetect(y, x, 3)
	
	# separando en fechas y precios 
	xm = [p[0] for p in _max]
	ym = [p[1] for p in _max]
	xn = [p[0] for p in _min]
	yn = [p[1] for p in _min]

	plot = plt.plot(x, y)
	plt.hold(True)
	plt.plot(xm, ym, "r+")
	plt.plot(xn, yn, "g+")
	
	# creando serie que contendra 0 cuando hay maximo, 
	# 1 cuando hay minimo y 2 cuando no hay ninguno.
	w2 = pd.Series(2,index=w.index)
	for date in xm: w2.loc[date] = 0
	for date in xn: w2.loc[date] = 1
	
	# creando serie binaria con el ideal de estrategia
	w3 = to_binary(w2)
	
	return w3


# funcion para convertir la serie con que contiene maximos (0), 
# minimos (1) y el resto (2) en una serie que solo contiene
# compro y tengo (1) y, vendo y espero (0)
def to_binary(w):
    #w2 = pd.Series(index=w.index, dtype=object)
    w2 = w.copy()
    w2[0] = 0
    for i in range(len(w)-1):
      if w2[i+1] != w2[i]:
        
        if w2[i] == 1 and w2[i+1]== 2:
            w2[i+1] = 1
        elif w2[i] == 0 and w2[i+1] == 2:
            w2[i+1] = 0
      else:
        pass
    
    return w2

