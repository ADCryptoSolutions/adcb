#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
import pandas as pd
#import pylab as plt
import numpy as np
from profit import change5
from orders import orders
from mldata import ml_data
from sklearn.linear_model import LogisticRegression
from core import movingAverage

# dada una serie de pandas o una lista, el tamaño de la ventanas de las medias móviles, y la definición de los tipos de series, devuelve vector w a partir de los cruces de las mismas.
def crossingStrategy(serie,serieType1=1,serieType2=2,longPeriod=20,shortPeriod=5):
    #La "serie1" suele escogerse como una serie en fase y/0 suavizada de "serie"
    if serieType1==0:
        serie1=serie
    elif serieType1==1:
        serie1=movingAverage(serie,longPeriod,1,0)#moving average centrada
    elif serieType1==2:
        serie1 = serie.ewm(span=shortPeriod, adjust=False).mean()#exponential moving average centrada rápida
    elif serieType1==3:
        serie1 = serie.ewm(span=longPeriod, adjust=False).mean()#exponential moving average centrada lenta
    
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

    
    """
    plt.figure()
    plt.plot(serie.index,serie,'g',label='precio')
    plt.plot(serie.index,ema,'r',label='EMA_%s'%emaPeriod)
    plt.plot(serie.index,sma,'b',label='EMA_%s'%smaPeriod)
    plt.legend(loc='best')
    plt.ylabel('Price (BTC)')
    plt.grid()
    plt.show()
    """
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
	
