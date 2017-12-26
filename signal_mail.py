#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Envía correo con información obtenida del liveBot 
v(1) 2017-12-25
autor: Daniel Siervo
e-mail: emetdan@gmail.com
"""

import smtplib 
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import system


def correo(order, date, pair, close, coin_balance, btc_balance, balance):

    hour = date.split(" ")[1]
    day = date.split(" ")[0]
	
    #lee datos del remitente
    datosr = open('../.remitente.txt','r').readlines()
    
    #Prepara correos electrónicos con información del sismo.boletin
    print 'Preparando correo...'
    remitente = datosr[0].strip(" ").strip("\n")
    passw = datosr[1].strip(" ").strip("\n")
    
    destinatario = "emetdan@gmail.com, sbuelvasch@gmail.com, eegutierrezb@gmail.com"
    asunto = "Orden %s puesta en %s"%(order, pair) 
    mensaje1=open('mail_message.txt').read()%(order, hour, day, pair, close, pair.split("_")[1], coin_balance, pair.split("_")[0], btc_balance, balance, pair.split("_")[0])
    
    #Prepara asunto y remitentes
    msg = MIMEMultipart()
    msg['Subject'] = asunto
    msg['From'] = datosr[0]
    
    #Prepara destinatarios y adjunta imagen
    msg['To'] = destinatario
    #fp=open(mapa, 'rb')
    #img = MIMEImage(fp.read())
    #fp.close()
    #msg.attach(img)
    text = MIMEText(mensaje1)
    print mensaje1
    msg.attach(text)    

    #inicia servicio de envío de correos
    server = smtplib.SMTP('smtp.gmail.com:587') 
    server.starttls()
    server.login(remitente,passw)

    server.sendmail(remitente, destinatario.split(", "), msg.as_string())
    print 'Enviando correo...'

    server.quit()

if __name__ == "__main__":
	
	order, date, pair, close, coin_balance, btc_balance, balance = "BUY", "2017-12-25 23:55:00", "BTC_DGB", str(0.00000500), str(2000), str(0.0), str(0.0002) 
	
	correo(order, date, pair, close, coin_balance, btc_balance, balance)
