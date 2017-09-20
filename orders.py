#-*-coding:utf-8-*-
import pandas as pd
# recibe el data frame w (pesos) y a grega a este
# la columna order con wait, sell o buy dependiendo el caso
def orders(w):
    w2 = pd.Series(index=w.index, dtype=object)
    if w[0] == 0:
            w2[0]= "WAIT"
    for i in range(len(w)-1):
      if w[i+1] != w[i]:
        
        if w[i+1] == 1:
            w2[i+1] = "BUY"
        elif w[i+1] == 0:
            w2[i+1] = "SELL"
      else:
        w2[i+1] = "WAIT"
    
    return w2
