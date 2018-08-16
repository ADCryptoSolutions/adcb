#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
import sys, getopt
from tusp import string2ts, ts2string
import pandas as pd
import numpy as np

def main(argv):
    """
    funcion principal
    """
    
    # cargando opciones del programa
    pair, start, end, period, strategy = load_BT_options(argv)
    #start = string2ts(start)
    #end = string2ts(end)
    print "\n"+pair, start, end, period, strategy+"\n"
    # inicializando Dataframe
    df = 0
    
    # lista de estrategias de machine learning
    ml_strategies = ["ml_logreg", "ml_randfor", "ml_knn", "ml_mlpc", "ml_bm"]
    # variable que se usa en run_strategy
    ml_strategy = False
    
    per = 0.95
    # si la estrategia es de machine learning
    if strategy in ml_strategies:
        ml_strategy = True
        # recalculando el tiempo inicial en virtud del entrenamiento del
        # algoritmo 
        start = ml_init_time(end,start,per)
        # cargando y preparando datos
        df = prepareData(pair=pair, start=start, end=end, period=period)
    else:
        df = prepareData(pair=pair, start=start, end=end, period=period)
    
    
    # Generando backTesting con las opciones de usuario
    #  Corriendo estrategia
    w, market_return = run_strategy(strategy,df,pair,ml_strategy,per)
    backTest(w, market_return, strategy)


def load_BT_options(argv):
    '''
    funcion que carga opciones de usuario
    '''
    currencyPair, start, end = "BTC_DGB", string2ts("2017-06-01 00:00:00"), string2ts("2017-09-01 00:00:00")
    period, strategy = 3600*4,"EMAvsSMA"
    try:
        opts, args = getopt.getopt(argv,"hp:c:n:s:e:f:s:",["period=","currency=","points="])
    except getopt.GetoptError:
        print ' Error trading-bot.py -p <period length> -c <currency pair> -s <start time> -e <end time> --> "YYYY:MM:DD hh:mm:ss"\
         -f <input file bot.inp> -s <back testing strategy>'
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print 'trading-bot.py -p <period length> -c <currency pair> -s <start time> -e <end time> --> "YYYY:MM:DD hh:mm:ss"\
         -f <input file> -s <back testing strategy>'
            sys.exit()
        elif opt in ("-p", "--period"):
            if (int(arg) in [300,900,1800,7200,14400,86400]):
                period = arg
            else:
                print 'Poloniex requires periods in 300,900,1800,7200,14400, or 86400 second increments'
                sys.exit(2)
        elif opt in ("-c", "--currency"):
            currencyPair = arg
        elif opt in ("-n", "--points"):
            lengthOfMA = int(arg)
        elif opt in ("-i"):
            ts = string2ts(arg)
            start = str(ts)
        elif opt in ("-e"):
            ts = string2ts(arg)
            end = str(ts)
        elif opt in ("-f"):
            dic = {}
            inputFile = open(arg).readlines()
            
            for line in inputFile:
              if line != ['']:
                k = line.split('=')
                dic[k[0].strip()] = k[1].strip().strip('\n')
            currencyPair = dic["currencyPair"]
            start = string2ts(dic["start"])
            end = string2ts(dic["end"])
            period = int(dic["period"])
            strategy = dic["strategy"]
        elif opt in ("-s"):
            strategy = arg
    if len(opts) == 0:
        print "No proporcionó opciones. Se tomarán las predeterminadas."
    return currencyPair, start, end, period, strategy


def prepareData(pair="DGB_BTC", start=string2ts("2017-06-01 00:00:00"), 
                 end=string2ts("2017-09-01 00:00:00"), period=3600*4):
    
    """
    funcion que trae los datos y 
    los devuleve en dataframe de pandas
    """

    from poloniex import Poloniex
    #import json
    #import pylab as plt
    
    #print conn.returnBalances()['BTC']
    polo = Poloniex()
    # historyData es una lista de diccionarios python
    # candlestick period in seconds; valid values are 300, 900, 1800, 7200, 14400, and 86400
    historyData = polo.returnChartData(currencyPair=pair,
                         start=start,
                         end=end,
                         period=period)

    # convirtiendo datos en data frame
    df = pd.DataFrame(historyData)

    #  convirtiendo string a float o int
    df["close"] =pd.to_numeric(df['close'])
    df["open"] =pd.to_numeric(df['open'])
    df["low"] =pd.to_numeric(df['low'])
    df["volume"] =pd.to_numeric(df['volume'])
    df["date"] = pd.to_datetime(df["date"].apply(ts2string))
    df['weightedAverage'] = pd.to_numeric(df['weightedAverage'])
    df['high'] = pd.to_numeric(df['high'])
    df['open'] = pd.to_numeric(df['open'])
    
    # calculando volatilidad en función del tamaño de las velas
    df["volatility"] = makeVolatility(df)

    # seleccionando la columna de fecha como indice
    df = df.set_index("date")
    
    return df


def makeVolatility(df, c=2.0, type=0):
    """
    Calcula la volatilidad en función  del tamaño de las velas
    """
    volatile = 0
    if type ==0:
        # distancia entre el precio más alto y el más bajo
        highLow = abs(df["high"]-df["low"])
        # distancia entre el precio de apertura y el de cierre
        openClose = abs(df["open"]-df["close"])
        
        volatile = highLow <= c*openClose
    if type ==1:
        from stockstats import StockDataFrame
        
        # Creando indicadores para estrategia, via stockstats
        stock = StockDataFrame.retype(df.copy())
        volatile = stock["pdi"]>c
        
    return volatile


def marketReturn(serie):
    
    # calculando los log retornos
    log_return = np.log(serie).diff().fillna(0)
    
    # calculando log retorno acumulado
    cum_logr = log_return.cumsum()
    cum_r = np.exp(cum_logr) - 1
    
    return cum_r

    """         
    poloKeys = open("../.kp").readlines()            
    conn = Poloniex(poloKeys[0].strip(),poloKeys[1].strip())
    print conn.returnBalances()['BTC']
    """

def run_strategy(strategy,df,pair,ml_strategy,per, typ=None):
    from strategy2 import pricevsEMA, pricevsSMA, EMAvsEMA, EMAvsSMA
    from strategy2 import SMAvsSMA, EMAvsSMA2, SMAvsSMA2
    from strategy2 import ml_randfor, ml_logreg, ml_knn, ml_mlpc, ml_bm
    from strategy2 import ml_xgb, ml_stacking, ml_period, train_ml_period
    from strategy import crossingStrategy, crossingStrategy2
    fun_dic = {
      "pricevsEMA": pricevsEMA,
      "pricevsSMA": pricevsSMA,
      "SMAvsSMA": SMAvsSMA,
      "SMAvsSMA2": SMAvsSMA2,
      "EMAvsSMA": EMAvsSMA,
      "EMAvsSMA2": EMAvsSMA2,
      "EMAvsEMA": EMAvsEMA,
      "ml_logreg": ml_logreg,
      "ml_randfor": ml_randfor,
      "ml_knn": ml_knn,
      "ml_mlpc": ml_mlpc,
      "ml_bm": ml_bm,
      "ml_xgb": ml_xgb,
      "ml_stacking": ml_stacking,
      "crossing":crossingStrategy,
      "crossing2":crossingStrategy2,
      "ml_period":ml_period
      }
    
    #ml_strategies = ["ml_logreg", "ml_randfor"]
    
    w=0
    feature_dic = {}
    
    if ml_strategy:
        from stockstats import StockDataFrame
        from indicators import rsi

        # Creando indicadores para estrategia, via stockstats
        stock = StockDataFrame.retype(df.copy())
        
        # el diccionario de caracterísitcas para ml_period solo cuenta con
        # 2 elementos
        if strategy[:9] == "ml_period":
            
            ts_1 = df.shift(1)
            ts_2 = df.shift(2)
            ts_3 = df.shift(3)
            tf_1 = df.shift(-1)
            
            df["feat1"] = ts_1["close"] > ts_2["close"]
            df["feat2"] = ts_2["close"] > ts_3["close"]
            
            #df["feat1"] = df["close"] > ts_1["close"]
            #df["feat2"] = df["close"] > ts_2["close"]
            
            outcome = (tf_1["close"]>tf_1["open"])
            
            feature_dic = {"feat1": df["feat1"], "feat2":df["feat2"], 
                           "rsi":stock["rsi_14"].shift(-1), 
                           "cci":stock["cci"].shift(-1)}
            
            if strategy == "ml_period2" and typ == "train":
                    
                    model, test = train_ml_period(df["close"], outcome,
                           per=per, **feature_dic)
                    return model, test


            # Creando vector de pesos utilizando estrategia de ML
            w = fun_dic[strategy](df["close"], outcome,
                       per=per, **feature_dic)
            
        else:
            #stock["rsi_14"];
            stock["cci"];
            
            RSI1, RSI2 = rsi(df["close"])
            
            # Caracteristicas sobre las que se entrenara el modelo
            feature_dic = {"log_return":marketReturn(df["close"]), "rsi":stock["rsi_14"],
                           "macd":stock["macd"],"macds":stock["macds"],"cci":stock["cci"],
                              "wr":stock["wr_14"], "trix":stock["trix"],
                              "vr":stock["vr"]}

            # Creando vector de pesos utilizando estrategia de ML
            w = fun_dic[strategy](df["close"], per=per, **feature_dic)
        
        #print df_rsi.isnull().any()
        #print df_rsi[df_rsi['RS1'].isnull()]
                
    else:
        # creando vector de pesos correspondiente 
        # a la estrategia i.e. cuando se compra y 
        # cuando se vende.
        try:
			# si la estrategia incluye filtro por volatilidad
			if strategy == "EMAvsSMA2" or strategy == "SMAvsSMA2" or strategy == "crossing2":
				w = fun_dic[strategy](df["close"],df["volatility"])
			else:
				w = fun_dic[strategy](df["close"])
        except KeyError:
            print "\n La estrategia %s no es valida. Las estrategias disponibles son:\n"%strategy
            for key in fun_dic.keys():
                print "\t"+key
            print "\n"
            sys.exit(1)
    # calculando el retorno del mercado en el tiempo seleccionado
    df["cum_r"] = marketReturn(w["price"])

    return w,df["cum_r"]
    
            
def backTest(w,cum_r,strategy):
    """
    Función para crear un back testing 
    de una estrategia dada. Muestra el profit en la pantalla.
    """
    from profit import profit
    
    #calculando el retorno relativo de la estrategia
    relativeReturn, vecReturn = profit(w)
    
    # graficando el retorno del mercado y el de la estrategia
    """"
    plt.figure()
    plt.plot(serie.index,serie['cum_r']*100,'b', label='Mercado %s'%pair)
    plt.plot(serie.index,vecReturn*100,'r', label='%s'%strategy)
    plt.legend(loc='best')
    plt.ylabel('Retorno relativo (%)')
    plt.title('Retorno del mercado vs estrategia')
    plt.grid()
    plt.show()
    """
    print_full(w[["orders","price","return"]])
    print "Retorno final del mercado: %s"%(cum_r[-1]*100)
    print 'El retorno final de la estrategia %s fue: %s'%(strategy,relativeReturn*100)

    
def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')


def ml_init_time(end,start,per):
    """genera el tiempo inicial que se requiere para las estrategias de ML
    ts1,ts2 = string, fechas en linux time stamp format
    """
    from datetime import datetime
    import time
    
    tf = datetime.fromtimestamp(end)
    ti = datetime.fromtimestamp(start)
    
    #print "per: %s, 1-Per: %s, Pocentaje Test-Train %s\n"%(per,1-per,int(1/(1-per)))
    
    # se utiliza round para corregir el problema de precision binaria
    t = tf-(tf-ti)*int(round(1/(1-per)))
    
    #print "Nuevo tiempo inicial %s\n"%t
    t_tuple = t.timetuple()
    
    return int(time.mktime(t_tuple))


def prepareLiveData(pair="DGB_BTC", start=string2ts("2017-06-01 00:00:00"), 
                 end=string2ts("2017-09-01 00:00:00"), period=3600*4):
    
    """
    funcion que trae los datos y 
    los devuleve en dataframe de pandas
    """

    from poloniex import Poloniex
    #import json
    #import pylab as plt
    
    poloKeys = open("../.kp").readlines()            
    polo = Poloniex(poloKeys[0].strip(),poloKeys[1].strip())
    #print conn.returnBalances()['BTC']
    #polo = Poloniex()
    # historyData es una lista de diccionarios python
    # candlestick period in seconds; valid values are 300, 900, 1800, 7200, 14400, and 86400
    historyData = polo.returnChartData(currencyPair=pair,
                         start=start,
                         end=end,
                         period=period)

    # convirtiendo datos en data frame
    df = pd.DataFrame(historyData)

    #  convirtiendo string a float o int
    df["close"] =pd.to_numeric(df['close'])
    df["open"] =pd.to_numeric(df['open'])
    df["low"] =pd.to_numeric(df['low'])
    df["volume"] =pd.to_numeric(df['volume'])
    df["date"] = pd.to_datetime(df["date"].apply(ts2string))
    df['weightedAverage'] = pd.to_numeric(df['weightedAverage'])
    df['high'] = pd.to_numeric(df['high'])
    df['open'] = pd.to_numeric(df['open'])
    
    # calculando volatilidad en función del tamaño de las velas
    df["volatility"] = makeVolatility(df)

    # seleccionando la columna de fecha como indice
    df = df.set_index("date")
    
    return df, polo


def sortino_ratio(rets):
	""" Calcula en ratio de Sortino
	
	"""

	semi_var = rets[rets < 0] ** 2
	semi_var = semi_var.sum()/len(rets)
	sortino = np.sqrt(semi_var)

	return rets.mean()/sortino
	
	
if __name__ == "__main__":
    main(sys.argv[1:])


