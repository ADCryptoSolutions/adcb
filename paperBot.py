#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------

import sys, getopt
from bot import prepareData, run_strategy
from tusp import string2ts

def main(argv):
    """
    funcion principal
    """
    
    # cargando opciones del programa
    pair, period, strategy = load_PT_options(argv)
    
    print "\n\tLas opciones cargadas fueron:\n" 
    print pair, period, strategy
    
    print "\n\n\tEjecutando Paper Trading\n\n"
    paper(pair, int(period), strategy)


def paper(pair, period, strategy): 
    """
    Traer los datos en vivo y devuelve SELL, WAIT o BUY,
    según la estrategia que se escoja    
    """
    
    # funciones necesarias para el manejo del tiempo
    from datetime import datetime, timedelta
    from time import sleep
    
    # en esta lista deben guardarse los nombres de todas las estrategias
    # de machine learning en strategy, para discriminar en base a estas
    # la cantindad de datos a traer
    ml_strategies = ["ml_logreg", "ml_randfor", "ml_knn"]
    
    delta = timedelta(seconds = period)
    
    ml_strategy = False
    have_coin = False
    len_data = 0

    # en el caso de una estrategía de ML porcentaje de datos que se utilizanran 
    # en el conjunto de datos de entrenamiento
    per = 0.95
    # dinero inicial con el que empieza el paperBot
    btc_balance = 1.0
    coin_balance = 0.0
    # definiendo el tiempo inicial de la consulta 
    if strategy in ml_strategies:
        # para estrategias de machine learning se tomarán los últimos
        # 7000 datos
        len_data = 7000
        ml_strategy = True
    else: 
        # para estrategias diferentes a las de ML se toman los últimos
        # 50 datos
        len_data = 50

    while True:
        try:        
            # definiendo end como el tiempo UTC actual
            tf = datetime.utcnow()
            end = string2ts(tf.strftime('%Y-%m-%d %H:%M:%S'))
            start = end 
            
            # definiendo el tiempo inicial de la consulta 
            to = tf-delta*len_data
            start = string2ts(to.strftime('%Y-%m-%d %H:%M:%S'))
                
            # trayendo y preparando datos
            df = prepareData(pair=pair, start=start, end=end, period=int(period))
            
            # corriendo estrategia. Generando vector w
            w, market_return = run_strategy(strategy,df,pair,ml_strategy,per)
            
            have_coin,coin_balance,btc_balance = run_paper_signal(tf.strftime('%Y-%m-%d %H:%M:%S'),w["orders"][-1],pair,df["close"][-1],have_coin,coin_balance,btc_balance)
            #print "%s %s %s %s %s\n"%(tf.strftime('%Y-%m-%d %H:%M:%S'),strategy,pair,w["orders"][-1],df["close"][-1])
            
            # se recarga cada period segundos
            sleep(period)
        
        # Saliendo del programa        
        except KeyboardInterrupt:
            
            yn = raw_input("\n\n\tDo you want to quit (y/n)? ")
            if yn == "y" or yn =="Y" or yn =="yes" or yn =="YES":
                print "\tSeleccionó salir. \n"
                balance = btc_balance+coin_balance*df["close"][-1]
                
                # guardando el resumen del paper trading en un archivo de texto
                with open("paper_resume_%s_%s_%s.txt"%(pair,strategy,period),"w") as paper_resume:
                    print >> paper_resume, "\tBalance: %s"%(balance)
                    print >> paper_resume, "\tProfit: {}%".format(round((balance-1)*100,2))
                
                print "\tBalance: %s"%(balance)
                print "\tProfit: {}%".format(round((balance-1)*100,2))
                print "\tHasta pronto..."
                sys.exit(1)
            elif yn == "n" or yn == "N" or yn == "no" or yn == "NO":
                print "\tSeleccionó seguir"
                pass

# imprime en pantalla deacuerdo a la señal dada
def run_paper_signal(time,signal,pair,close,have_coin,coin_balance,btc_balance):
    balance = btc_balance + coin_balance*close
    if signal == "WAIT":
        print time, pair, close, signal," ->balance:",round(balance,5),"BTC"
    
    elif signal == "SELL":
        if have_coin:
            btc_balance = coin_balance*close
            coin_balance = 0.0
            balance = btc_balance
            print time, pair, close, signal," ->balance:",round(balance,5),"COIN",coin_balance,"BTC",btc_balance
            have_coin = False
        else:
            #print "\nhave_coin: {}, not have_coin {}".format(have_coin,not have_coin)
            #print "No quizo vender el berraco"
            print "coin_balance: {}, btc_balance: {}".format(coin_balance,btc_balance)
            print time, pair, close, "WAIT"," ->balance:",round(balance,5),"BTC"
    
    elif signal == "BUY":
        if not have_coin:
            coin_balance = btc_balance/close
            btc_balance = 0.0
            balance = coin_balance*close
            print time, pair, close, signal," ->balance:",round(balance,5),"COIN:",coin_balance,"BTC:",btc_balance
            have_coin = True
        else:
            #print "\nhave_coin: {}, not have_coin {}".format(have_coin,not have_coin)
            #print "No quizo comprar el berraco"
            print time, pair, close, "WAIT"," ->balance:",round(balance,5),"BTC"
        
    return have_coin,coin_balance,btc_balance

def load_PT_options(argv):
    '''
    funcion que carga opciones de usuario de paper trading
    '''
    currencyPair, start, end = "BTC_DGB","2017-06-01 00:00:00","2017-06-01 00:00:00"
    period, strategy = 3600*4,"EMAvsSMA"
    try:
        opts, args = getopt.getopt(argv,"hp:c:n:s:e:f:s:",["period=","currency=","points="])
    except getopt.GetoptError:
        print '\t Error paperBot.py. The valid option are:\n -p <period length> -c <currency pair> -s <strategy> -h <help>'
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print 'paperBot.py -p <period length> -c <currency pair> -s <strategy>'
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
            period = int(dic["period"])
            strategy = dic["strategy"]
        elif opt in ("-s"):
            strategy = arg
    if len(opts) == 0:
        print "\n\tYou did not provide options. The default ones will be assumed.\n"
        print "paperBot.py -p <period length> -c <currency pair> -s <strategy>"
    return currencyPair, period, strategy

if __name__ == "__main__":
    main(sys.argv[1:])
