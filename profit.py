#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
# Funcion que calcula el profit de una determinada
# estrategia dados w y la serie correspondiente al precio
import numpy as np
import pandas as pd
from orders import orders

def profit(w):

  #print w.head(2)
  w['w'] = w['w'].shift(1)
  logReturn = np.log(w["price"]).diff().fillna(0)
  vecLogReturn = (logReturn*w["w"]).cumsum()
  vecReturn = np.exp(vecLogReturn.apply(pd.to_numeric))-1
  #relativeReturn = np.exp(np.dot(w["w"],logReturn)) - 1
  w["return"] = vecReturn
  return vecReturn[-1], vecReturn

def profit3(w):
    
    # Creando nueva columna con los precios
    w["price_profit"] = w["price"]
    # para la fila en que orders es BUY el precio será negativo
    w.loc[w["orders"] == "BUY","price_profit"] = w[w["orders"] == "BUY"]["price"]*-1
    # para la fila en que orders es WAIT el preico será 0
    w.loc[w["orders"] == "WAIT","price_profit"] = 0
    # se restan todos los precios de compra de los precios de venta y se divide entre el primer precio de compra
    vecReturn = (w["price_profit"].cumsum()/w[w["orders"] == "BUY"]["price"][0])
    relativeReturn = vecReturn[-1]
    return relativeReturn, vecReturn

def profit2(w,btc_init=1.0):

	fee = 0.0008	
	w["btc_balance"] = 0.0
	w.loc[:,"btc_balance"].values[0] = (1-w['w'][0])*btc_init
	w["coin_balance"] = w['w'][0]*btc_init/w['price'][0]
	w["balance"] = 0.0
	w.loc[:,"balance"].values[0] = w['coin_balance'][0]*w['price'][0]+w['btc_balance'][0]
	nbuys = 0
	nsells = 0	
	for i in range(1,len(w["btc_balance"])):
		
	    if w["w"][i]:
	      if w["coin_balance"][i-1] == 0.0:
    			nbuys +=1
    			w.loc[:,"coin_balance"].values[i] = (1-fee)*w["btc_balance"][i-1]/w["price"][i]
    			w.loc[:,"btc_balance"].values[i] = 0.0
	      else:
    			w.loc[:,"btc_balance"].values[i] = w["btc_balance"][i-1]
    			w.loc[:,"coin_balance"].values[i] = w["coin_balance"][i-1]
	    else:
	      if w["coin_balance"][i-1] != 0.0:
    			nsells +=1
    			w.loc[:,"btc_balance"].values[i] = (1-fee)*w["coin_balance"][i-1]*w["price"][i]
    			w.loc[:,"coin_balance"].values[i] = 0.0
	      else:
    			w.loc[:,"btc_balance"].values[i] = w["btc_balance"][i-1]
    			w.loc[:,"coin_balance"].values[i] = w["coin_balance"][i-1]

	    w.loc[:,"balance"].values[i] = w["btc_balance"][i] + w["coin_balance"][i]*w["price"][i]
	
	vecReturn = (w["balance"]-btc_init)/btc_init
	relativeReturn = vecReturn[-1]
	
	print "Compró y vendió un total de %s y %s veces, respectivamente"%(nbuys,nsells)
	return relativeReturn, vecReturn
	
			
# convierte el 0.5 que aparece al principio de w al hacer
# (dif+1)/2 en los casos en los que se empieza con la orden wait
# en 0.0			 
def change5(f):
    if f == 0.5:
        return 0.0
    else:
        return f
