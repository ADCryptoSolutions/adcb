#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
import pandas as pd
#import pylab as plt
import numpy as np
from profit import change5
from orders import orders
from mldata import ml_data
from sklearn.linear_model import LogisticRegression

# dada una serie de pandas o una lista y el numero de muestras para la EMA y SMA devuelve vector w
# considerando el cruce entre EMA y SMA
def EMAvsSMA(serie, smaPeriod=20,emaPeriod=5):
        
    # Calculando media movil a 20 muestras
    sma = serie.rolling(smaPeriod,min_periods=1).mean()
    # caculando exponential movil average
    ema = serie.ewm(span=emaPeriod, adjust=False).mean()
    
    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)
    
    w = pd.DataFrame(data={"w":(dif+1)/2})
    
    w['w'] = w['w'].apply(change5)
    
    w["orders"] = orders(w["w"])
    w['w'] = w['w'].shift(1)
    w["price"] = serie
    
    """
    plt.figure()
    plt.plot(serie.index,serie,'g',label='precio')
    plt.plot(serie.index,ema,'r',label='EMA_%s'%emaPeriod)
    plt.plot(serie.index,sma,'b',label='SMA_%s'%smaPeriod)
    plt.legend(loc='best')
    plt.ylabel('Price (BTC)')
    plt.grid()
    plt.show()
    """
    return w

# dada una serie de pandas y el numero de muestras para las EMAs devuelve vector w
# considerando el cruce entre estas
def EMAvsEMA(serie, smaPeriod=20,emaPeriod=5):
    
    # caculando exponential movil average lenta
    sma = serie.ewm(span=smaPeriod, adjust=False).mean()
    # caculando exponential movil average rapida
    ema = serie.ewm(span=emaPeriod, adjust=False).mean()
    
    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)
    
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

# dada una serie de pandas y el numero de muestras para la EMA devuelve vector w
# considerando el cruce entre EMA y el precio
def pricevsEMA(serie, emaPeriod=5):
    
    # precio
    ema = serie
    # caculando exponential movil average rapida
    sma = serie.ewm(span=emaPeriod, adjust=False).mean()
    
    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)
    
    w = pd.DataFrame(data={"w":(dif+1)/2})
    
    w['w'] = w['w'].apply(change5)
    
    w["orders"] = orders(w["w"])
    w['w'] = w['w'].shift(1)
    w["price"] = serie
    """
    plt.figure()
    plt.plot(serie.index,serie,'g',label='precio')
    plt.plot(serie.index,sma,'r',label='EMA_%s'%emaPeriod)
    plt.legend(loc='best')
    plt.ylabel('Price (BTC)')
    plt.grid()
    plt.show()
    """
    return w

# dada una serie de pandas y el numero de muestras para la EMA devuelve vector w
# considerando el cruce entre EMA y el precio
def pricevsSMA(serie, smaPeriod=20):
    
    # precio
    ema = serie
    # Calculando media movil a 20 muestras
    sma = serie.rolling(smaPeriod,min_periods=1).mean()
    
    # Encontrando el signo de la resta entre ellas para encontrar los cruces
    dif = (ema - sma).apply(np.sign)
    
    w = pd.DataFrame(data={"w":(dif+1)/2})
    
    w['w'] = w['w'].apply(change5)
    
    w["orders"] = orders(w["w"])
    w['w'] = w['w'].shift(1)
    w["price"] = serie
    """
    plt.figure()
    plt.plot(serie.index,serie,'g',label='precio')
    plt.plot(serie.index,sma,'b',label='SMA_%s'%smaPeriod)
    plt.legend(loc='best')
    plt.ylabel('Price (BTC)')
    plt.grid()
    plt.show()
    """
    return w
 
def ml_logreg(close,per=0.9,**kwargs):
	"""
	close: Serie de Pandas con precio de cierre. Se utiliza para crear
	       la estrategia ideal.
	per: Float que especifica en que porcentaje se dividiran train y test.
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
	logreg.fit(train.drop(["best_w","close"],axis=1),train["best_w"])
	# prediciendo con el modelo
	pred = logreg.predict(test.drop(["best_w","close"],axis=1))
	
	# dataframe con vector de pesos de estrategia de regresio logistica
	w_pred = pd.DataFrame(data={"w":pred,"price":test["close"]})
	w_pred["orders"] = orders(w_pred["w"])
	w_pred["w"] = w_pred["w"].shift(1)
	
	return w_pred
	
