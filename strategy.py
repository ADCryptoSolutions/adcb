#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
import pandas as pd
#import pylab as plt
import numpy as np
from profit import change5
from orders import orders, volatility_corection
from mldata import ml_data
from sklearn.linear_model import LogisticRegression
from core import movingAverage

# dada una serie de pandas o una lista, el tamaño de la ventanas de las medias móviles, y la definición de los tipos de series, devuelve vector w a partir de los cruces de las mismas.
def crossingStrategy(serie,serieType1=1,serieType2=2,longPeriod=5,shortPeriod=3):
    
    #La "serie1" suele escogerse como una serie en fase y/0 suavizada de "serie"
    if serieType1==0:
        serie1=serie
    elif serieType1==1:
        serie1=movingAverage(serie,longPeriod,1,0)#moving average centrada
    elif serieType1==2:
        serie1 = serie.ewm(span=shortPeriod, adjust=False).mean()#exponential moving average centrada rápida
    elif serieType1==3:
        serie1 = serie.ewm(span=longPeriod, adjust=False).mean()#exponential moving average centrada lenta
    elif serieType1==4:
        serie1=movingAverage(serie,longPeriod,1,-1)#moving average adelantada(como rolling)
    elif serieType1==5:
        serie1=movingAverage(serie,longPeriod,1,1) #moving average atrasada% 
    
    
    #La "serie2" suele escogerse como una serie desfasada suavizada de "serie".    
    if serieType2==0:
        serie2=serie
    elif serieType2==1:
        serie2=movingAverage(serie,longPeriod,1,0)#moving average centrada
    elif serieType2==2:
        serie2 = serie.ewm(span=shortPeriod, adjust=False).mean()#exponential moving average centrada rápida
    elif serieType2==3:
        serie2 = serie.ewm(span=longPeriod, adjust=False).mean()#exponential moving average centrada lenta
    elif serieType2==4:
        serie2=movingAverage(serie,longPeriod,1,-1)#moving average adelantada(como rolling)
    elif serieType2==5:
        serie2=movingAverage(serie,longPeriod,1,1) #moving average atrasada 
    
    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (serie1 - serie2).apply(np.sign)
    
    w = pd.DataFrame(data={"w":(dif+1)/2})
    
    w['w'] = w['w'].apply(change5)
    
    w["orders"] = orders(w["w"])
    w['w'] = w['w'].shift(1)
    w["price"] = serie  

    return w


# dada una serie de pandas o una lista, el tamaño de la ventanas de las medias móviles, y la definición de los tipos de series, devuelve vector w a partir de los cruces de las mismas.
def crossingStrategy2(serie, volatility, serieType1=1,serieType2=2,longPeriod=5,shortPeriod=3):
    #La "serie1" suele escogerse como una serie en fase y/0 suavizada de "serie"
    if serieType1==0:
        serie1=serie
    elif serieType1==1:
        serie1=movingAverage(serie,longPeriod,1,0)#moving average centrada
    elif serieType1==2:
        serie1 = serie.ewm(span=shortPeriod, adjust=False).mean()#exponential moving average centrada rápida
    elif serieType1==3:
        serie1 = serie.ewm(span=longPeriod, adjust=False).mean()#exponential moving average centrada lenta
    elif serieType1==4:
        serie2=movingAverage(serie,longPeriod,1,-1)#moving average adelantada(como rolling)
    elif serieType1==5:
        serie2=movingAverage(serie,longPeriod,1,1) #moving average atrasada 
    
    
    #La "serie2" suele escogerse como una serie desfasada suavizada de "serie".    
    if serieType2==0:
        serie2=serie
    elif serieType2==1:
        serie2=movingAverage(serie,longPeriod,1,0)#moving average centrada
    elif serieType2==2:
        serie2 = serie.ewm(span=shortPeriod, adjust=False).mean()#exponential moving average centrada rápida
    elif serieType2==3:
        serie2 = serie.ewm(span=longPeriod, adjust=False).mean()#exponential moving average centrada lenta
    elif serieType2==4:
        serie2=movingAverage(serie,longPeriod,1,-1)#moving average adelantada(como rolling)
    elif serieType2==5:
        serie2=movingAverage(serie,longPeriod,1,1) #moving average atrasada 
    
    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (serie1 - serie2).apply(np.sign)
    
    w = pd.DataFrame(data={"w":(dif+1)/2})
    
    w['w'] = w['w'].apply(change5)

    # corrigiendo por volatilidad
    w["w"] = volatility_corection(w["w"], volatility)
    
    w["orders"] = orders(w["w"])
    w['w'] = w['w'].shift(1)
    w["price"] = serie  

    return w


def ml_logreg(close,per=0.9,**kwargs):
	"""
	Estrategia basada en un modelo de regresion logistica.
	
	close: Serie de Pandas con precio de cierre. Se utiliza para crear
	       la estrategia ideal.
	per: Float que especifica en que porcentaje se dividiran los datos para train y test.
	**kwargs: Diccionario con las caracteristicas para entrenar y predecir.
	"""
	
	# dataframe con pesos de la estrategia ideal
	w = pd.DataFrame(data={"w":ml_data(close,pl=False).values,"price":close})
	w["orders"] = orders(w["w"])
	# vector de pesos de la estrategia ideal
	w['w'] = w['w'].shift(1)
	
	# diccionario que contendra las caracteristicas para evaluar y 
	# el precio o weightedAverage sobre el que se quiere predecir
	dic = {"best_w":w["w"],"close":close}
	# agregando el resto de las caracteristicas
	dic.update(kwargs)
	
	# creando dataframe con los valores del diccionario
	data = pd.DataFrame(data=dic)
	
	# separando datos para crear y evaluar el modelo de machine learning.
	# se toma train desde 1 para no tener NaN de la primera fila
	train = data[1:int(len(data)*per)]
	test = data[int(len(data)*per):]
	
	# iniciando modelo de regresion logistica
	logreg = LogisticRegression()
	# entrenando el modelo
	try:
		logreg.fit(train.drop(["best_w","close"],axis=1),train["best_w"])
	except ValueError:
		print train.isnull().any()
		print train[train['rsi'].isnull()]
	# prediciendo con el modelo
	pred = logreg.predict(test.drop(["best_w","close"],axis=1))
	
	# dataframe con vector de pesos de estrategia de regresio logistica
	w_pred = pd.DataFrame(data={"w":pred,"price":test["close"]})
	w_pred["orders"] = orders(w_pred["w"])
	w_pred["w"] = w_pred["w"].shift(1)
	
	return w_pred


def hf(buy_price, sell_price, current_price, gain_rate = 0.02, lose_rate = 0.01, have_coin=False,sell_fee=0.0025,buy_fee=0.0025):
	"""dfda
	afadsfa
	"""
	
	signal = "WAIT"
	# si queremos vender
	if have_coin:
		if current_price*(1-sell_fee) > (buy_price*(1+gain_rate)):
			signal = "SELL"
			sell_price = current_price*(1-sell_fee)
		elif buy_price*(1-lose_rate) > (current_price)*(1-sell_fee):
			signal = "SELL"
			sell_price = current_price*(1-sell_fee)
		else:
			signal = "WAIT"
	
	else:
		print "En hf: ",sell_price*(1-lose_rate), current_price
		if (sell_price*(1-lose_rate)) > current_price*(1-buy_fee):
			 signal = "BUY"
			 buy_price = current_price*(1-buy_fee)
		else:
			signal = "WAIT"

	return signal, buy_price, sell_price
