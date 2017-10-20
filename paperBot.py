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
	

# Traer los datos en vivo y devolver SELL, WAIT o BUY,
# según la estrategia que se escoja	
def live(): 
	

if __name__ == "__main__":
	main(sys.argv[1:])
