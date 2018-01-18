#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------

import sys, getopt
from bot import run_strategy, prepareLiveData
from tusp import string2ts
from signal_mail import correo


def main(argv):
    """
    funcion principal 
    """
    
    # cargando opciones del programa
    pair, period, strategy, weight = load_PT_options(argv)
    
    print "\n\tLas opciones cargadas fueron:\n" 
    print pair, period, strategy, "Weight: %s"%weight
    
    print "\n\n\tEjecutando Live Trading\n\n"
    paper(pair, int(period), strategy, weight)


def paper(pair, period, strategy, weight): 
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
    # máximo delay aceptado entre el tiempo actual y el del último dato
    delta2 = timedelta(seconds = 180)
    # desfase para en la mayoría de los casos no entrar al while
    delta3 = timedelta(seconds = 90)
    ml_strategy = False
    have_coin = False
    len_data = 0
    # en el caso de una estrategía de ML porcentaje de datos que se utilizanran 
    # en el conjunto de datos de entrenamiento
    per = 0.95
    # dinero inicial con el que empieza el paperBot
    balance = []
    # definiendo el tiempo inicial de la consulta 
    if strategy in ml_strategies:
        # para estrategias de machine learning se tomarán los últimos
        # 7000 datos
        len_data = 7000
        ml_strategy = True
    else: 
        # para estrategias diferentes a las de ML se toman los últimos
        # 50 datos
        len_data = 40

    while True:
        try:        
            # definiendo end como la hora local actual
            tf = datetime.now()
            # convirtiendola a formato unix time (es equivalente a UTC)
            end = string2ts(tf.strftime('%Y-%m-%d %H:%M:%S'))
            #start = end 
            
            # definiendo el tiempo inicial de la consulta 
            to = tf-delta*len_data
            start = string2ts(to.strftime('%Y-%m-%d %H:%M:%S'))
                
            # trayendo y preparando datos
            df, polo = prepareLiveData(pair=pair, start=start, end=end, period=int(period))
            #print "El total de datos descargados es: ",len(df)
            # corriendo estrategia. Generando vector w
            tt = df.index[-1]
            de = tf - tt
            
            # sincronizando tiempo del bot
            if de > delta2:
                # mientras la diferencia entre el la hora del último precio de cierre y
                # y la hora actual sea mayor a 120s
                while de > delta2:
    
                    # definiendo end como la hora local actual
                    tf = datetime.now()
                    # convirtiendola a formato unix time (es equivalente a UTC)
                    end = string2ts(tf.strftime('%Y-%m-%d %H:%M:%S')) 
                    to = tf-delta*len_data
                    start = string2ts(to.strftime('%Y-%m-%d %H:%M:%S'))
                    # trayendo y preparando datos
                    df, polo = prepareLiveData(pair=pair, start=start, end=end, period=int(period))
                    tt = df.index[-1]
                    de = tf - tt
                    sys.stdout.write("\rSincronizando bot (delay máximo aceptado 120s, actual %ss). Esperando cierre de las %s. Último dato de cierre a las %s"%(str((de).seconds), str(tt+delta), str(tt)))
                    sys.stdout.flush()
                    sleep(15)
            
            print "\n"
            
            #corriendo estrategia
            w, market_return = run_strategy(strategy,df,pair,ml_strategy,per)
            
            have_coin,coin_balance,btc_balance, order = run_live_signal(polo, str(df.index[-1]),w["orders"][-1],pair, df["close"][-1], have_coin, strategy, balance, weight)
            #print "%s %s %s %s %s\n"%(tf.strftime('%Y-%m-%d %H:%M:%S'),strategy,pair,w["orders"][-1],df["close"][-1])
            # calibrando tiempo de espera de acuerdo a emisión de próximo dato
            tf = datetime.now()
            to_sleep = tt+delta-tf+delta3
            # se recarga cada to_sleep segundos
            sleep(to_sleep.seconds)
        
        # Saliendo del programa        
        except KeyboardInterrupt:
            
            yn = raw_input("\n\n\tDo you want to quit (y/n)? ")
            if yn == "y" or yn =="Y" or yn =="yes" or yn =="YES":
                print "\tSeleccionó salir. \n" 
                
                # guardando el resumen del paper trading en un archivo de texto
                with open("paper_resume_%s_%s_%s.txt"%(pair, strategy, period),"w") as paper_resume:
                    try:
                        print >> paper_resume, "\tBalance: %s"%(balance[-1])
                    except IndexError:
                        print "\tHasta pronto..."
                        sys.exit()
                    print >> paper_resume, "\tProfit: {}%".format(round((balance[-1]-balance[0])/balance[0]*100, 2))
                
                print "\tBalance: %s"%(balance[-1])
                print "\tProfit: {}%".format(round((balance[-1]-balance[0])/balance[0]*100,2))
                print "\tHasta pronto..."
                bot_off(polo, order)
            elif yn == "n" or yn == "N" or yn == "no" or yn == "NO":
                print "\tSeleccionó seguir"
                pass

# imprime en pantalla deacuerdo a la señal dada
def run_live_signal(polo, time, signal, pair, close, have_coin, strategy, balance, weight):
    
    fee = 0.0025
    btc_balance = float(polo.returnBalances()[pair.split("_")[0]])
    coin_balance = float(polo.returnBalances()[pair.split("_")[1]])
    balance.append(btc_balance + coin_balance*close)
    
    destinatarios = open("destinatarios.txt").read()
    
    
    if coin_balance >= 0.00001: have_coin = True
    else: have_coin = False
    
    order = []
    
    if signal == "WAIT":
        print time, pair, close, signal," ->balance:",round(balance[-1], 6),"BTC"
    
    elif signal == "SELL":
        if have_coin:
            # colocando orden de venta de todas las monedas que tenemos 
            # para el par deseado, al último precio de cierre.
            order = polo.sell(pair, close, coin_balance)
            btc_balance = coin_balance*close*(1-fee)
            coin_balance = 0.0
            balance[-1] = btc_balance
            print "\n\tEstrategia: ",strategy,"\n"
            print time, pair, close, signal," ->balance:",round(balance[-1], 6),"COIN",coin_balance,"BTC",btc_balance
            correo(signal, time, pair, close, coin_balance, btc_balance, balance[-1], strategy, destinatarios)
        else:
            print time, pair, close, "WAIT"," ->balance:",round(balance[-1], 6),"BTC"
    
    elif signal == "BUY":
        if not have_coin:
            # colocando orden de compra de todas las monedas que tenemos 
            # para el par deseado, al último precio de cierre.
            try:
                order = polo.buy(pair, close, (btc_balance*weight)/close)
            except:
                print "Error al comprar"
                print "have_coin",have_coin,"close",close,"btc_balance",btc_balance
            coin_balance = (btc_balance/close)*(1-fee)
            btc_balance = 0.0
            balance[-1] = coin_balance*close
            print "\n\tEstrategia: ",strategy,"\n"
            print time, pair, close, signal," ->balance:",round(balance[-1], 6),"COIN:",coin_balance,"BTC:",btc_balance
            correo(signal, time, pair, close, coin_balance, btc_balance, balance[-1], strategy, destinatarios)
        else:
            #print "\nhave_coin: {}, not have_coin {}".format(have_coin,not have_coin)
            #print "No quizo comprar el berraco"
            print time, pair, close, "WAIT"," ->balance:",round(balance[-1], 6),"BTC"
        
        # supervisando que la extrategia no esté perdiendo más del 10%
        trading_supervisor(polo, balance, order)
        
    return have_coin, coin_balance, btc_balance, order


def load_PT_options(argv):
    '''
    funcion que carga opciones de usuario de paper trading
    '''
    currencyPair, start, end = "BTC_DGB","2017-06-01 00:00:00","2017-06-01 00:00:00"
    period, strategy = 300,"EMAvsSMA"
    weight = 1.0
    try:
        opts, args = getopt.getopt(argv,"hp:c:n:s:e:f:s:w:",["period=","currency=","points="])
    except getopt.GetoptError:
        print '\t Error paperBot.py. The valid option are:\n -p <period length> -c <currency pair> -s <strategy> -w <weight> -h <help>'
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print 'liveBot.py -p <period length> -c <currency pair> -s <strategy>'
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
        elif opt in ("-w","--weight"):
            weight = float(arg)
    if len(opts) == 0:
        print "\n\tYou did not provide options. The default ones will be assumed.\n"
        print "paperBot.py -p <period length> -c <currency pair> -s <strategy> -w <weight>"
    return currencyPair, period, strategy, weight

def trading_supervisor(polo, balance, order):
    if order != []:
        if balance[-1] <= -10:
            print "\t\nCancelando ordenes abiertas y parando el bot debido a bajo rendimiento\n"
            bot_off(polo, order)

def bot_off(polo, order):
    if order != []:
        cancel_order = polo.cancelOrder(order["orderNumber"])
    sys.exit()

if __name__ == "__main__":
    main(sys.argv[1:])
