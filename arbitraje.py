#-*-coding:utf-8-*-
# ---- emetdan@gmail.com -------

import sys


if len(sys.argv) != 5:
	print "\t\nEl programa requiere de 4 argumentos\n"
	print "\t Pusd, TRM, Pb, b\n"
	print "Dolares a pasar a Advcash, Tasa representativa del mercado COP/USD, \
Precio del BTC en localbitcoin o SurBTC, BTC que pide Advcash por Pusd\n"
	sys.exit(1)

# Dolares a pasar a Advcash
Pusd = float(sys.argv[1])
# Tasa representativa del mercado COP/USD
TRM = float(sys.argv[2])
# Precio del Bitcoin en local bitcoin o SurBTC
Pb = float(sys.argv[3])
# BTC que pide Advcash por Pusd
b = float(sys.argv[4])

b2 = ((Pusd*(1.0-0.0295)-2.99-1500/TRM)*TRM)/Pb

Entrar = False

if b2 >= b + (Pusd*0.05)/Pb:
	Entrar = True

# BTC comprados menos los vendidos
b3 = (b2-b)

print "\n\tLos bitcoins que se ganarian o perderian serian: %s\n"%b3
print "\tEl dinero que ganariamos o perderíamos en COP es: %s\n"%(b3*Pb)
print "\tSe obtiene un profit de: %s"%(b3/b*100)
print "\tDeberiamos hacer la operacion? --> %s\n"%Entrar



	
