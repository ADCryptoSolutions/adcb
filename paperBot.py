#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------

from bot import load_options, prepareData, marketReturn
from tusp import string2ts, ts2string
import sys


def main(argv):
	"""
	funcion principal
	"""
	
	# cargando opciones del programa
	pair, start, end, period, strategy = load_options(argv)
	
	print "\nLas opciones cargadas fueron:\n" 
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
	
	len_data = 0
	
	# definiendo el tiempo inicial de la consulta 
	if strategy in ml_strategies:
		# para estrategias de machine learning se tomarán los últimos
		# 5000 datos
		len_data = 5000
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
			
			print "%s periodo %ss %s %s %s\n"%(tf.strftime('%Y-%m-%d %H:%M:%S'),period,pair,strategy,df["close"][-1])
			# se recarga cada period segundos
			sleep(period)
		
		# Saliendo del programa		
		except KeyboardInterrupt:
			
			yn = raw_input("\n\n\tAre you sure you want to quit (y/n)? ")
			if yn == "y" or yn =="Y" or yn =="yes" or yn =="YES":
				print "\tSeleccionó %s. Hasta pronto.."%yn
				sys.exit(1)
			elif yn == "n" or yn == "N" or yn == "no" or yn == "NO":
				print "\tSeleccionó %s"%yn
				pass
	
if __name__ == "__main__":
	main(sys.argv[1:])
