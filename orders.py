# -*-coding:utf-8-*-

import pandas as pd


def orders(w):
    # recibe el data frame w (pesos) y a grega a este
    # la columna order con wait, sell o buy dependiendo el caso
    w2 = pd.Series(index=w.index, dtype=object)
    if w[0] == 0:
            w2[0] = "WAIT"
    for i in range(len(w)-1):
      if w[i+1] != w[i]:
        if w[i+1] == 1:
            w2[i+1] = "BUY"
        elif w[i+1] == 0:
            w2[i+1] = "SELL"
      else:
        w2[i+1] = "WAIT"

    return w2


def volatility_corection(w, volatility):
    """
    Corrige un vector de pesos derivado de una estrategia de cruce de medias
    vteniendo en cuenta la volatilidad de la vela en los cruces.

    w: Vector o serie de pandas con ceros o unos
    volatility: vector o serie de pandas con True o False dependiendo si
    es volatil o no
    """

    #w2 = pd.Series(index=w.index, dtype=object)
    w2 = w.copy()

    volatile = False

    # recoriendo la serie
    for i in range(len(w)-1):
        # si quiere comprar o vender
        if w[i+1] != w[i]:
            # miro la volatilidad en el cruce
            volatile = volatility[i+1]

            # si es volatil en el cruce -> no opere
            if volatile:
                w2[i+1] = w[i]
    
    return w2
