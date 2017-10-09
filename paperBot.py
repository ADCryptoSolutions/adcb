#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------

from bot import load_options, prepareData, marketReturn

def main(argv):
	"""
	funcion principal
	"""
	
	# cargando opciones del programa
	pair, start, end, period, strategy = load_options(argv)
	
	# trayendo y preparando datos
	df = prepareData(pair=pair, start=start, end=end, period=period)
	
	# calculando retorno del mercado
	cumReturn = marketReturn(df)
	marketReturn = cumReturn[-1]*100
	 
	

if __name__ == "__main__":
	main(sys.argv[1:])
