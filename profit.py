#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
# Funcion que calcula el profit de una determinada
# estrategia dados w y la serie correspondiente al precio
import numpy as np

def profit2(w,p):
  
  logReturn = np.log(p).diff().fillna(0)
  vecLogReturn = (logReturn*w).cumsum()
  vecReturn = np.exp(vecLogReturn)-1
  relativeReturn = np.exp(np.dot(w,logReturn)) - 1
  return relativeReturn, vecReturn

# convierte el 0.5 que aparece al principio de w al hacer
# (dif+1)/2 en los casos en los que se empieza con la orden wait
# en 0.0
def profit(w):
    
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

def profit3(w):
	
	btc_balance = w["price"].copy()
	coin_balance = btc_balance.copy()
	
	coin_balance[0] = 0
	
	for i in range(1,len(l2)):
		if w["orders"][i] == "BUY":
			coin_balance[i] = btc_balance[i]/w["price"][i]
			btc_balance[i] = 0
		elif w["orders"][i] == "SELL":
			btc_balance[i] = coin_balance[i]*w["price"]
			coin_balance[i] = 0
		elif w["orders"][i] == "WAIT":
			btc_balance[i] = btc_balance[i-1]
			coin_balance[i] = coin_balance[i-1]
	
	balance = btc_balance + coin_balance*w["price"]
	
	vecReturn = balance/w[w["orders"] == "BUY"]["price"][0]
	relativeReturn = vecReturn[-1]
	
	return relativeReturn, vecReturn
	
			
			 

def change5(f):
    if f == 0.5:
        return 0.0
    else:
        return f
