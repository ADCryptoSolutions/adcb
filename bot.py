#-*-coding:utf-8-*-
#!/home/daniel/anaconda2/bin/python python
# ---- emetdan@gmail.com -------
    
import time
import sys, getopt
import datetime
from poloniex import Poloniex
from tusp import string2ts, ts2string
import pylab as pl
import pandas as pd

def main(argv):
	period = 10
	currencyPair = "BTC_XML"
	prices = []
	currentMovingAverage = 0;
	lengthOfMA = 0
	startTime = False
	endTime = False
	historicalData = False
	tradePlaced = False
	typeOfTrade = False
	dataDate = ""
	orderNumber = ""
	load_options(argv)


def load_options(argv):
	try:
		opts, args = getopt.getopt(argv,"hp:c:n:s:e:f:",["period=","currency=","points="])
	except getopt.GetoptError:
		print ' Error trading-bot.py -p <period length>\n -c <currency pair>\n -s <start time> -e <end time> --> "YYYY:MM:DD hh:mm:ss"\
		 -f <input file bot.inp>'
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print 'trading-bot.py -p <period length> -c <currency pair> -s <start time> -e <end time> --> "YYYY:MM:DD hh:mm:ss"\
		 -f <input file>'
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
	
	return currencyPair, start, end, period
	
	"""		 
	poloKeys = open("../.kp").readlines()			
	conn = Poloniex(poloKeys[0].strip(),poloKeys[1].strip())
	print conn.returnBalances()['BTC']
	"""
	
	# Función para crear un back testing de alguna estrategia
	def backTest(pair, start, end, period, coins=10):
		
		# Iniciando el objeto Poloniex de forma pública
		polo = Poloniex()
		
		# Si existe tiempo inicial
		if (start):
			historicalData = polo.returnChartData(currencyPair = currencyPair, start=start , end=end, period=period)
		
		#if historicalData:
			

if __name__ == "__main__":
	main(sys.argv[1:])


