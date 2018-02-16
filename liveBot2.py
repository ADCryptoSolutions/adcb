# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 21:34:55 2018

@author: Daniel David Siervo Plata <emetdan@gmail.com>
"""
from datetime import timedelta, datetime
from time import sleep
from tusp import string2ts
from bot import run_strategy, prepareLiveData
import sys
from publicano import Publicano
from liveBot import bot_off, trading_supervisor
from signal_mail import correo


class LiveBot:

    def __init__(self, pair, period, strategy, checker=None):

        self.pair = pair
        self.period = period
        self.strategy = strategy
        self.checker = checker
        self.counter = 0

        # en estrategía de ML, porcentaje de datos que se utilizaran
        # en el conjunto de datos de entrenamiento
        self.per = 0.95
        # en esta lista deben guardarse los nombres de todas las estrategias
        # de machine learning en strategy, para discriminar en base a estas
        # la cantindad de datos a traer
        self.ml_strategies = ["ml_logreg", "ml_randfor", "ml_knn"]
        self.ml_strategy = False
        self.have_coin = False
        self.delta = timedelta(seconds=int(self.period))
        # máximo delay aceptado entre el tiempo actual y el del último dato
        self.delta2 = timedelta(seconds=200)
        # desfase para en la mayoría de los casos no entrar al while
        self.delta3 = timedelta(seconds=90)

        self.len_data = 0
        # dinero inicial con el que empieza el paperBot
        self.balance = []
        # definiendo el tiempo inicial de la consulta

        print "Creado live Bot con las siguientes características:\n"
        print "\tpair: {0}, period: {1}, strategy: {2}, checker: {3}\n".format(self.pair,
                       self.period, self.strategy, self.checker)

    def prepareData(self):
        """Trae el dataframe y el objeto poloniex correspondiente"""

        # definiendo end como la hora local actual
        self.tf = datetime.now()
        # convirtiendola a formato unix time (es equivalente a UTC)
        self.end = string2ts(self.tf.strftime('%Y-%m-%d %H:%M:%S'))

        # definiendo el tiempo inicial de la consulta
        self.to = self.tf-self.delta*self.len_data
        self.start = string2ts(self.to.strftime('%Y-%m-%d %H:%M:%S'))

        # trayendo y preparando datos
        self.df, self.polo = prepareLiveData(pair=self.pair, start=self.start,
                                             end=self.end, period=int(self.period))

        # fecha del último dato disponible
        self.tt = self.df.index[-1]
        # delay entre el tiempo actual y el último dato disponible
        self.de = self.tf - self.tt

    def lenData(self):
        """Define la cantidad de datos a traer de acuerdo si la estrategia es
        o no de machine learning
        """

        if self.strategy in self.ml_strategies:
            # para estrategias de machine learning se tomarán los últimos
            # 7000 datos
            self.len_data = 7000
            self.ml_strategy = True
        else:
            # para estrategias diferentes a las de ML se toman los últimos
            # 50 datos
            self.len_data = 40

    def timeSincronizator(self):
        """Trae los datos (dataFrame y objeto polo) siempre y cuando el delay
        entre el tiempo actual y el últimio dato en el dataFrame no sea mayor
        a 200 segundos (delta2). Sincroniza el tiempo del bot"""

        # definiendo self.tf, self.end, self.to, self.start, self.tt, self.de
        self.prepareData()

        # sincronizando tiempo del bot
        if self.de > self.delta2:
            # mientras la diferencia entre el la hora del último precio de
            # cierre y la hora actual sea mayor a 120s
            while self.de > self.delta2:
                self.prepareData()
                sys.stdout.write("\rSincronizando bot (delay máximo aceptado\
                                200s, actual %ss). Esperando cierre de las %s.\
                                Último dato de cierre a las %s"%(str((self.de).seconds),
                                str(self.tt+self.delta), str(self.tt)))
                sys.stdout.flush()
                sleep(5)

        print "\n"

    def startBot(self):
        """Inicia el bot y lo mantiene en un cilo de periodo self.period"""

        if self.checker is not None:
            # al crear a checker se genera el archivo fundTracker.inp que
            # contiene los monto que se le dieron a cada bot para que administrara
            self.checker = Publicano(base_coin=self.pair.split("_")[0])

        # definiendo la self.len_data y self.ml_strategy
        self.lenData()
        while True:
            try:
                # Trayendo datos sincronizados (crea dataFrame, objeto polo y
                # variables temporales)
                self.timeSincronizator()

                # corriendo estrategia
                self.w, self.market_return = run_strategy(self.strategy,
                                                          self.df, self.pair,
                                                          self.ml_strategy,
                                                          self.per)

                self.signal, self.close = self.w["orders"][-1], self.df["close"][-1]

                # operando en el exchange de acuerdo a la señal obtenida,
                # muestra en pantalla y envía correo con un resumen de la operación.
                # Verifica si está en multiBot y de acuerdo a esto modifica el monto
                # disponible para compra
                self.run_live_signal()

                self.counter += 1

                # calibrando tiempo de espera de acuerdo a emisión de próximo dato
                to_sleep = self.tt+self.delta-self.tf+self.delta3
                # se recarga cada to_sleep segundos
                sleep(to_sleep.seconds)

            # Saliendo del programa
            except KeyboardInterrupt:

                yn = raw_input("\n\n\tDo you want to quit (y/n)? ")
                if yn == "y" or yn == "Y" or yn == "yes" or yn == "YES":
                    print "\tSeleccionó salir. \n"

                    # guardando el resumen del paper trading en un archivo de texto
                    with open("paper_resume_%s_%s_%s.txt"%(self.pair,
                                                           self.strategy,
                                                           self.period), "w") as paper_resume:
                        try:
                            print >> paper_resume, "\tBalance: %s"%(self.balance[-1])
                        except IndexError:
                            print "\tHasta pronto..."
                            sys.exit()
                        print >> paper_resume, "\tProfit: {}%".format(round((self.balance[-1]-self.balance[0])/self.balance[0]*100, 2))

                    print "\tBalance: %s"%(self.balance[-1])
                    print "\tProfit: {}%".format(round((self.balance[-1]-self.balance[0])/self.balance[0]*100,2))
                    print "\tHasta pronto..."
                    bot_off(self.polo, self.order)
                elif yn == "n" or yn == "N" or yn == "no" or yn == "NO":
                    print "\tSeleccionó seguir"
                    pass

    def run_live_signal(self):
        """Ejecuta en el exchange, muestra en pantalla
        y envía correo de acuerdo a la señal dada por la estrategia
        :type btc_balance: float
        :param btc_balance: bitcoins disponibles para comprar el par
        """

        # dinero que se dispone para compra del activo
        base_balance = 0.0
        polo = self.polo
        pair = self.pair
        time = str(self.tt)
        # desatrasando el vector de pesos (se atrasó para el cálculo del
        # retorno vía log_retornos)
        w = self.w["w"][-1]
        signal = self.signal
        close = self.close
        base_simbol = pair.split("_")[0]

        coin_balance = float(polo.returnBalances()[pair.split("_")[1]])
        fee = 0.0025

        # si se está trabajando con un solo bot y con el balance total
        if self.checker is None:
            # seleccionando como balance de compra el balance
            # total en la moneda base
            base_balance = float(self.polo.returnBalances()[pair.split("_")[0]])
            self.balance.append(base_balance + coin_balance*close)

        # si está trabajando con otros bots o con montos parciales
        else:
            # si es la primera vez que el bot opera debe utilizar la primera
            # fila del fundTracker.inp (fila que crea initFundTracker)
            if self.counter == 0:
                # creando primera linea en fundTracker.inp, de acuerdo a
                # los pesos en multiBot.inp
                self.checker.initFundTracker(time, self.polo)
                # leyendo como diccionario el primer dato de fundTracker.inp
                # y de acuerdo esto seleccionando el dinero disponible para comprar
                base_balance = float(self.checker.fundTrackerReader()[0][self.pair])
            else:
                # leyendo balance de compra del archivo personal
                base_balance = float(self.read_balance())

            self.balance.append(base_balance)

        balance = self.balance

        # escribiendo último balance en archivo de texto
        destinatarios = open("destinatarios.txt").read()

        # corroborando si poseemos o no el activo
        if coin_balance >= 0.00001:
            self.have_coin = True
        else:
            self.have_coin = False

        self.order = []

        print "W:", w, "have_coin:", self.have_coin
        # si según la señal no deberíamos poseer el activo
        if not w:
            # pero lo tenemos
            if self.have_coin:
                # colocando orden de venta de todas las monedas que tenemos
                # para el par deseado, al último precio de cierre.
                # self.order = polo.sell(pair, close, coin_balance)
                base_balance = coin_balance*close*(1-fee)
                coin_balance = 0.0
                balance[-1] = base_balance
                print "\n\tEstrategia: ", self.strategy, "\n"
                print time, pair, close, signal," ->balance:",round(balance[-1], 6),"COIN",coin_balance,base_simbol+":",base_balance
                # correo(signal, time, pair, close, coin_balance,
                       #base_balance, balance[-1], self.strategy, destinatarios)
            # si no lo tenemos
            else:
                print time, pair, close, "WAIT"," ->balance:", round(balance[-1], 6), base_simbol

        # si según la señal deberíamos poseer el activo
        elif w:
            # y no lo tenemos
            if not self.have_coin:
                # colocando orden de compra de todas las monedas que tenemos
                # para el par deseado, al último precio de cierre.
                try:
                    print "En try"
                    # self.order = polo.buy(pair, close, (base_balance)/close)
                except:
                    print "Error al comprar"
                    print "have_coin",self.have_coin,"close",close,"base_balance",base_balance
                coin_balance = (base_balance/close)*(1-fee)
                base_balance = 0.0
                balance[-1] = coin_balance*close
                print "\n\tEstrategia: ", self.strategy, "\n"
                print time, pair, close, signal," ->balance:",round(balance[-1], 6),"COIN:",coin_balance,base_simbol+":",base_balance
                # correo(signal, time, pair, close, coin_balance,
                       #base_balance, balance[-1], self.strategy, destinatarios)
            # si lo tenemos
            else:
                print time, pair, close, "WAIT"," ->balance:",round(balance[-1], 6),base_simbol

            # supervisando que la extrategia no esté perdiendo más del 10%
        print "En trading_supervisor"
        trading_supervisor(polo, balance, self.order)

        # escribiendo en archivo de texto el último balance
        print "Escribiendo balance administrado en archivo de texto"
        self.write_balance()

        # actualizando el balance del bot
        self.balance = balance

    def write_balance(self):
        """Escribe en un archivo de texto el último balance de los fondos
        administrados por el bot"""

        with open(self.pair+"_bot.txt", "w") as f:
            f.write(str(self.balance[-1]))

    def read_balance(self):
        """Lee de un archivo de texto el último balance de los fondos
        administrados por el bot"""

        balance = open(self.pair+"_bot.txt").readlines()

        return balance[0]


if __name__ == "__main__":

    TestBot = LiveBot("BTC_DGB", "300", "ml_knn", checker=True)
    TestBot.startBot()
