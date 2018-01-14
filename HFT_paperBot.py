#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------

from poloniex import Poloniex
import sys, getopt
from bot import prepareData, run_strategy
from tusp import string2ts
from paperBot import run_paper_signal
from strategy import hf

def main(argv):
    """
    funcion principal
    """
    
    # cargando opciones del programa
    pair, gain_rate, lose_rate, period = load_PT_options(argv)
    
    print "\n\tLas opciones cargadas fueron:\n" 
    print pair, gain_rate, lose_rate, period
    
    print "\n\n\tEjecutando Paper Trading\n\n"
    paper(pair, gain_rate, lose_rate, period)


def paper(pair, gain_rate, lose_rate, period): 
    """
    Traer los datos en vivo y devuelve SELL, WAIT o BUY,
    según la estrategia que se escoja    
    """
    
    # funciones necesarias para el manejo del tiempo
    from datetime import datetime, timedelta
    from time import sleep
     
    delta = timedelta(seconds = period)    
    have_coin = False
    # dinero inicial con el que empieza el paperBot
    btc_balance = 1.0
    coin_balance = 0.0
    polo = Poloniex()
    buy_price = float(polo.returnTicker()[pair]["last"])
    sell_price = 1.5*buy_price


    while True:
        try:        
            # definiendo end como la hora local actual
            tf = datetime.now()
            
            # trayendo el ultimo dato y convirtiendolo en float
            tickers = polo.returnTicker()[pair]
            ticker = float(tickers["last"])
            
            signal, buy_price, sell_price = hf(buy_price, sell_price, ticker, gain_rate, lose_rate, have_coin)
            
            have_coin, coin_balance, btc_balance = run_paper_signal(tf.strftime('%Y-%m-%d %H:%M:%S'), signal, pair, ticker, have_coin, coin_balance, btc_balance)
            #print "%s %s %s %s %s\n"%(tf.strftime('%Y-%m-%d %H:%M:%S'),strategy,pair,w["orders"][-1],df["close"][-1])
            
            # se recarga cada period segundos
            sleep(period)
        
        # Saliendo del programa        
        except KeyboardInterrupt:
            
            yn = raw_input("\n\n\tDo you want to quit (y/n)? ")
            if yn == "y" or yn =="Y" or yn =="yes" or yn =="YES":
                print "\tSeleccionó salir. \n"
                balance = btc_balance+coin_balance*ticker
                
                # guardando el resumen del paper trading en un archivo de texto
                with open("paper_resume_HF_%s_%s.txt"%(pair,period),"w") as paper_resume:
                    print >> paper_resume, "\tBalance: %s"%(balance)
                    print >> paper_resume, "\tProfit: {}%".format(round((balance-1)*100,2))
                
                print "\tBalance: %s"%(balance)
                print "\tProfit: {}%".format(round((balance-1)*100,2))
                print "\tHasta pronto..."
                sys.exit(1)
            elif yn == "n" or yn == "N" or yn == "no" or yn == "NO":
                print "\tSeleccionó seguir"
                pass


def load_PT_options(argv):
    '''
    funcion que carga opciones de usuario de paper trading
    '''
    pair, gain_rate, lose_rate, period = "BTC_DGB", 0.02, 0.01, 1
    try:
        opts, args = getopt.getopt(argv,"h:p:c:g:l:e:f:s:",["period=","currency=","gain_rate=","lose_rate="])
    except getopt.GetoptError:
        print '\t Error paperBot.py. The valid option are:\n -p <period length> -c <currency pair> -g <gain_rate> -l <lose_rate> -h <help>'
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print 'HFT_paperBot.py -c <currency pair> -p <period> -g <gain rate> -l <lose rate>'
            sys.exit()
        elif opt in ("-p", "--period"):
			period = arg
        elif opt in ("-c", "--currency"):
            pair = arg
        elif opt in ("-g", "--gain_rate"):
            gain_rate = float(arg)
        elif opt in ("-l","--lose_rate"):
            lose_rate = float(arg)
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
        elif opt in ("-s"):
            strategy = arg
    if len(opts) == 0:
        print "\n\tYou did not provide options. The default ones will be assumed.\n"
        print 'HFT_paperBot.py -c <currency pair> -p <period> -g <gain rate> -l <lose rate>'
    return pair, gain_rate, lose_rate, period

if __name__ == "__main__":
    main(sys.argv[1:])
