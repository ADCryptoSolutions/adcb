#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------
import sys, getopt
from tusp import string2ts, ts2string
import pandas as pd

def main(argv):
	"""
	funcion principal
	"""
	
	# cargando opciones del programa
	pair, start, end, period, strategy = load_options(argv)
	
	# cargando y preparando datos
	df = prepareData(pair=pair, start=start, end=end, period=period)
	
	# Generando backTesting con las opciones de usuario
	backTest(strategy,df,pair)


def load_options(argv):
	'''
	funcion que carga opciones de usuario
	'''
	
	try:
		opts, args = getopt.getopt(argv,"hp:c:n:s:e:f:s:",["period=","currency=","points="])
	except getopt.GetoptError:
		print ' Error trading-bot.py -p <period length>\n -c <currency pair>\n -s <start time> -e <end time> --> "YYYY:MM:DD hh:mm:ss"\
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
			pair = arg
		elif opt in ("-n", "--points"):
			lengthOfMA = int(arg)
		elif opt in ("-s"):
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
	return currencyPair, start, end, period, strategy


def prepareData(pair="DGB_BTC", start=string2ts("2017-06-01 00:00:00"), 
                 end=string2ts("2017-09-01 00:00:00"), period=3600*4):
	
	"""
	funcion que trae los datos y 
	los devuleve en dataframe de pandas
	"""

	from poloniex import Poloniex
	import json
	import numpy as np
	#import pylab as plt
	
	
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
	df["low"] =pd.to_numeric(df['high'])
	df["volume"] =pd.to_numeric(df['volume'])
	df["date"] = pd.to_datetime(df["date"].apply(ts2string))
	df['weightedAverage'] = pd.to_numeric(df['weightedAverage'])

	# seleccionando la columna de fecha como indice
	df = df.set_index("date")
	
	# Calculando retornos relativos
	# el 1 se refiere al numero de periodos que se toma para calcular el cambio porcentual
	df["retornos relativos"] = df["close"].pct_change(1).fillna(0)

	# calculando los log retornos
	df["log retornos"] = np.log(df["close"]).diff().fillna(0)

	# calculando log retorno acumulado
	df["cum_logr"] = df["log retornos"].cumsum()
	df["cum_r"] = np.exp(df["cum_logr"]) - 1
	
	return df

	
	"""		 
	poloKeys = open("../.kp").readlines()			
	conn = Poloniex(poloKeys[0].strip(),poloKeys[1].strip())
	print conn.returnBalances()['BTC']
	"""
	
def backTest(strategy,serie,pair):
	from strategy import pricevsEMA,pricevsSMA,EMAvsEMA,EMAvsSMA
	fun_dic = {
	  "pricevsEMA":pricevsEMA,
	  "pricevsSMA":pricevsSMA,
	  "EMAvsSMA":EMAvsSMA,
	  "EMAvsEMA":EMAvsEMA
	  }
	
	"""
	Función para crear un back testing 
	de una estrategia dada
	"""
	
	from profit import profit
	
	# creando vector de pesos correspondiente 
	# a la estrategia i.e. cuando se compra y 
	# cuando se vende.
	w = fun_dic[strategy](serie["close"])
	
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
	print "Retorno final del mercado: %s"%(serie["cum_r"][-1]*100)
	print 'El retorno final de la estrategia %s fue: %s'%(strategy,relativeReturn*100)

    
def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')

if __name__ == "__main__":
	main(sys.argv[1:])


