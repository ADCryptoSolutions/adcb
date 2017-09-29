#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
import pandas as pd
#import pylab as plt
import numpy as np
from profit import change5
from orders import orders

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
