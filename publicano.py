# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 21:22:44 2018

@author: Daniel
"""


class Publicano():

    def __init__(self, tracker_file="fundTracker.inp", base_coin="BTC"):
        """Clase que administra el funcionamiento de varios bots a la vez
        Requiere el archivo multi_bot.inp con la estructura sugerida
        en la función bot_loader

        :param tracker_file: nombre del archivo que llevará el seguimiento a
        los fondos manejados por los bots.
        :type tracker_file: string
        """

        self.base_coin = base_coin
        self.tracker_file = tracker_file
        self.bot_loader()
        self.n_bots = len(self.bots)
        self.fundTrackerConstructor()

    def bot_loader(self):
        """Carga los datos para crear los bots desde el archivo
        multi_bot.inp, cuyo formato por línea es:
        par, %, estrategia, periodo
        """
        bots = []

        # abriendo archivo como lista
        multi_file = open("multi_bot.inp").readlines()

        for line in multi_file:
            if line.strip("\n").strip(" ") != "":
                pair = line.split(",")[0].strip(" ")
                weight = line.split(",")[1].strip(" ")
                strategy = line.split(",")[2].strip(" ")
                period = line.split(",")[3].strip("\n").strip(" ")
                bots.append({"pair": pair, "weight": weight,
                             "strategy": strategy, "period": period})

        self.bots = bots

        # Lista con todos los pares del MultiBot
        pairs = []
        for bot in bots:
            pairs.append(bot["pair"])

        self.pairs = pairs

    def fundTrackerConstructor(self):
        """Crea archivo fundTracker con su header."""

        bots = ""
        for bot in self.bots:
            bots += bot["pair"]+"_"+bot["strategy"]+bot["period"]+","


        with open(self.tracker_file, "w") as tracker_file:
            tracker_file.write("Fecha,"+bots.strip(",")+"\n")

    def fundTrackerWriter(self, fecha, balances):
        """Escribe la distribución de los fondos administrados por
        cada bot en el archivo fundTracker.inp, cuyo formato por linea es:
        Fecha, balance par_1, balance par_2, ..., balance par_n

        :param fecha: Fecha de la linea de balance a escribir
        :type fecha: string con formato YYYY-mm-dd hh:mm:ss

        :param balances: contiene el balance actual en cada par en la moneda base
        :type balances: lista de python. Los fondos en la lista deben
        seguir el orden de self.pairs"""

        # Se agrega linea al final del archivo con el último
        # dato de los balances
        with open(self.tracker_file, "a") as tracker_file:
            tracker_file.write(fecha+","+",".join(balances)+"\n")

    def fundTrackerReader(self):
        """Lee los fondos administrados por cada bot. Esto es,
        lee el archivo fundTracker.inp"""

        # Se abre el archivo fundTracker.inp como lista
        tracker_file = open(self.tracker_file).readlines()
        # Lista que contendrá diccionarios por cada fila de
        # datos en fundTracker.inp
        tracker_list = []
        # matriz con los datos del archivo
        balances = []

        # creando balances
        for line in tracker_file:
            balances.append(line.strip("\n").split(","))

        # obteniendo una lista con el header
        headers = balances[0][1:]

        # recorriendo la matriz para generar la lista con los diccionarios
        for row in range(1, len(balances)):
            # creando diccionario, cuyas llaves son un string con el par
            dic = {}
            for index, pair in enumerate(headers):
                dic[pair] = balances[row][index+1]
            # agregando diccionario a la lista
            tracker_list.append(dic)

        return tracker_list

    def initFundTracker(self, fecha, polo):
        """Calcula la distribución de los fondos (en la moneda base) de acuerdo
        a la información proporcionada en el tracker_file y al balance de la
        moneda base en poloniex (Primera linea de datos en el tracker_file)
        """
        self.init_balance = polo.returnBalances()[self.base_coin]

        balances = []

        # No estoy seguro que los escriba en el orden que es
        for bot in self.bots:
            balance = float(bot["weight"])*float(self.init_balance)
            balances.append(str(balance))

        self.fundTrackerWriter(fecha, balances)

    def fundTracker(self, fecha):
        """Lee los archivos individuales creados por cada bot y con esos datos
        hace la lista de balances para escribir el tracker_file"""

        # leyendo archivos individuales (deben estar en el mismo directorio de
        # los archivos de configuración)

        balances = []

        for pair in self.pairs:
            f = open(pair+"_bot.txt").readlines()
            balances.append(f[0])

        self.fundTrackerWriter(fecha, balances)
