#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------

from bot import load_options, prepareData, marketReturn, run_strategy
from tusp import string2ts, ts2string
import sys


def main(argv):
	"""
	funcion principal
	"""
	
	# cargando opciones del programa
	pair, start, end, period, strategy = load_options(argv)
	
	print "\n\tLas opciones cargadas fueron:\n" 
	print pair, period, strategy
	
	print "\n\n\tEjecutando Paper Trading\n\n"
	paper(pair, int(period), strategy)


def paper(pair, period, strategy): 
	"""
	Traer los datos en vivo y devolver SELL, WAIT o BUY,
	según la estrategia que se escoja	
	"""
	
	# funciones necesarias para el manejo del tiempo
	from datetime import datetime, timedelta
	from time import sleep
	
	# en esta lista deben guardarse los nombres de todas las estrategias
	# de machine learning en strategy, para discriminar en base a estas
	# la cantindad de datos a traer
	ml_strategies = ["ml_logreg"]
	
	delta = timedelta(seconds = period)
	
	ml_strategy = False
	have_coin = False
	len_data = 0
	per = 0.95
	# dinero inicial con el que empieza el paperBot
	btc_balance = 1.0
	coin_balance = 0.0
	# definiendo el tiempo inicial de la consulta 
	if strategy in ml_strategies:
		# para estrategias de machine learning se tomarán los últimos
		# 5000 datos
		len_data = 7000
		ml_strategy = True
	else: 
		# para estrategias diferentes a las de ML se toman los últimos
		# 50 datos
		len_data = 100

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
		print time, pair, close, signal," ->balance:",balance,"BTC"
	
	elif signal == "SELL":
		if have_coin:
			btc_balance = coin_balance*close
			coin_balance = 0.0
			balance = btc_balance
			print time, pair, close, signal," ->balance:",balance,"BTC"
			have_coin = False
		else:
			print time, pair, close, "WAIT"," ->balance:",balance,"BTC"
	
	elif signal == "BUY":
		if not have_coin:
			coin_balance = btc_balance/close
			btc_balance = 0.0
			balance = coin_balance*close
			print time, pair, close, signal," ->balance:",balance,"BTC"
			have_coin = True
		else:
			print "have_coin: {}, not have_coin {}".format(have_coin,not have_coin)
			print "No quizo comprar el berraco"
			print time, pair, close, "WAIT"," ->balance:",balance,"BTC"
		
	return have_coin,coin_balance,btc_balance

if __name__ == "__main__":
	main(sys.argv[1:])
