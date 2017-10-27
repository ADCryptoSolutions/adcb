#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
# Funcion que calcula el profit de una determinada
# estrategia dados w y la serie correspondiente al precio
import numpy as np

def profit(w):
  
  logReturn = np.log(w["price"]).diff().fillna(0)
  vecLogReturn = (logReturn*w["w"]).cumsum()
  vecReturn = np.exp(vecLogReturn)-1
  relativeReturn = np.exp(np.dot(w["w"],logReturn)) - 1
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

def profit2(w,btc_init=1):
	
	w["btc_balance"] = 0.0
	w.loc[:,"btc_balance"].values[0] = btc_init
	w["coin_balance"] = 0.0
	w["balance"] = 0.0
	w.loc[:,"balance"].values[0] = btc_init
	
	for i in range(1,len(w["btc_balance"])):
		
		if w["orders"][i] == "BUY":
			#w.loc[:,"coin_balance"].values[i] = 0.0
			#w.loc[:,"btc_balance"].values[i] = w["btc_balance"][i-1]
			w.loc[:,"coin_balance"].values[i] = w["btc_balance"][i-1]/w["price"][i]
			w.loc[:,"btc_balance"].values[i] = 0.0
		elif w["orders"][i] == "SELL":
			#w.loc[:,"btc_balance"].values[i] = 0.0
			#w.loc[:,"coin_balance"].values[i] = w["coin_balance"][i-1]
			w.loc[:,"btc_balance"].values[i] = w["coin_balance"][i-1]*w["price"][i]
			w.loc[:,"coin_balance"].values[i] = 0.0
		elif w["orders"][i] == "WAIT":
			w.loc[:,"btc_balance"].values[i] = w["btc_balance"][i-1]
			w.loc[:,"coin_balance"].values[i] = w["coin_balance"][i-1]
		
		w.loc[:,"balance"].values[i] = w["btc_balance"][i] + w["coin_balance"][i]*w["price"][i]
		#print w["balance"][i],w["btc_balance"][i],w["coin_balance"][i]
		#print w["btc_balance"][i] + w["coin_balance"][i]*w["price"][i]
	
	vecReturn = (w["balance"]-btc_init)/btc_init
	relativeReturn = vecReturn[-1]
	
	return relativeReturn, vecReturn
	
			
# convierte el 0.5 que aparece al principio de w al hacer
# (dif+1)/2 en los casos en los que se empieza con la orden wait
# en 0.0			 
def change5(f):
    if f == 0.5:
        return 0.0
    else:
        return f
