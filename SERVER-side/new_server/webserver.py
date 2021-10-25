# -*- coding: utf-8 -*-
#!/bin/env python
''' Webserver '''

import sys, signal, socket, socketserver, webbrowser, requests, csv, re
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer #eventualmente from http.server import BaseHTTPRequestHandler, HTTPServer

#Classe per definire le modalità GET e POST del nostro server
class Send(BaseHTTPRequestHandler):
    def do_GET(self):
        #print(self.client_address)
        #print(self.path)

        if('hostname' in str(self.path)):
            try:
                key = str(self.path).split('key=')[1].split('&')[0]
                #print(key)
                
                hostname = str(self.path).split('hostname=')[1].split('&')[0]
                #print(hostname)

                ip = str(self.path).split('ip=')[1]
                #print(ip)

                result = checkKey(key, hostname)
            except:
                result = 4

            if(result == 0):
                changeStatus(key, hostname, ip)
                self.send_response(200)
            elif(result == 1):
                self.send_response(503)
            elif(result == 2):
                self.send_response(201)
            elif(result == 3):
                self.send_response(504)
            elif(result == 4):
                self.send_response(404)
            
            self.end_headers()

        elif('bind' in str(self.path)):
            try:
                key = str(self.path).split('?key')[1].split('?name')[0]
                #print(key)

                discord_name = str(self.path).split('?name')[1].split('?id')[0].replace('%20',' ').strip().replace(':','#').strip()
                #print(discord_name)

                discord_id = str(self.path).split('?id')[1]
                #print(discord_id)

                result = setBind(key, discord_name, discord_id)
            except:
                result = 2

            if(result == 0):
                self.send_response(200)
            elif(result == 1):
                self.send_response(503)
            elif(result == 2):
                self.send_response(404)
            elif(result == 3):
                self.send_response(405)

            self.end_headers()
            
        elif('reset' in str(self.path)):
            try:
                key = str(self.path).split('?key')[1].split('?name')[0]
                print(key)

                discord_name = str(self.path).split('?name')[1].split('?id')[0].replace('%20',' ').strip().replace(':','#').strip()
                print(discord_name)

                discord_id = str(self.path).split('?id')[1]
                print(discord_id)

                result = resetKey(key, discord_name, discord_id)
            except:
                result = 2


            if(result == 0):
                self.send_response(200)
            elif(result == 1):
                self.send_response(503)
            elif(result == 2):
                self.send_response(404)
            elif(result == 3):
                self.send_response(405)

            self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

def setBind(key, discord_name, discord_id):
    with open('key.csv', 'r') as csv_file:
        csv_key = csv.DictReader(csv_file)

        for line in csv_key:
            #print(line['KEY'])
            if(line['KEY'] == key):
                if(line['DISCORD_NAME'] == ''):
                    changeDiscord(key, discord_name, discord_id)
                    return 0
                elif line['DISCORD_ID'] == discord_id:
                    return 3
                else:
                    return 1
        return 2

def checkKey(key, hostname):
     with open('key.csv', 'r') as csv_file:
        csv_key = csv.DictReader(csv_file)

        for line in csv_key:
            #print(line['KEY'])
            if(line['KEY'] == key):
                if(line['STATUS'] == 'OK') and (line['DISCORD_NAME'] != ''):
                    return 0    #OK CHIAVE BINDATA , DA COLLEGARE AL COMPUTER
                elif (line['STATUS'] == 'OK') and (line['DISCORD_NAME'] == ''):
                    return 1    #BISOGNA BINDARE DISCORD
                elif(line['STATUS'] == 'BINDED') and (line['HOSTNAME'] == hostname):
                    return 2    #OK BINDATA E STAI USANDO QUEL COMPUTER
                elif(line['STATUS'] == 'BINDED') and (line['HOSTNAME'] != hostname):
                    return 3    #OK BINDATA MA NON è LO STESSO COMPUTER
        return 4

def changeStatus(key, hostname, ip): 
    with open('key.csv', 'r') as csv_file:
        csv_key = csv.DictReader(csv_file)

        for line in csv_key:
            if(line['KEY'] == key):
                discord_name = line['DISCORD_NAME']
                discord_id = line['DISCORD_ID']

    text = open("key.csv", "r")
    text = ''.join([i for i in text]) \
        .replace('"'+key+'","OK","","","'+discord_name+'","'+discord_id+'"', '"'+key+'","BINDED","'+hostname+'","'+ip+'"'+',"'+discord_name+'","'+discord_id+'"')
    x = open("key.csv", "w")
    x.writelines(text)
    x.close()

def changeDiscord(key, discord_name, discord_id):
    text = open("key.csv", "r")
    text = ''.join([i for i in text]) \
        .replace('"'+key+'","OK","","","",""', '"'+key+'","OK","",""'+',"'+discord_name+'","'+discord_id+'"')
    x = open("key.csv", "w")
    x.writelines(text)
    x.close()

def resetKey(key, discord_name, discord_id):
    with open('key.csv', 'r') as csv_file:
        csv_key = csv.DictReader(csv_file)

        for line in csv_key:
            #print(line['KEY'])
            if(line['KEY'] == key):
                if(line['DISCORD_ID'] == discord_id):
                    if(line['HOSTNAME'] != ''):
                        text = open("key.csv", "r")
                        text = ''.join([i for i in text]) \
                            .replace('"'+key+'","BINDED","'+line['HOSTNAME']+'","'+line['IP_ADDRESS']+'","'+line['DISCORD_NAME']+'","'+discord_id+'"', '"'+key+'","OK","","","'+discord_name+'","'+discord_id+'"')
                        x = open("key.csv", "w")
                        x.writelines(text)
                        x.close()
                        return 0
                    else:
                        return 3
                else:
                    return 1
        return 2

#Funzione per lanciare il Server
def run(handler_class=Send, port=5000):
    server_address = ('', port)
    #Creiamo il server con address:port e la classe precedentemente definita per gestire GET e POST request
    server = socketserver.ThreadingTCPServer(server_address, handler_class)

    #Assicura che da tastiera usando la combinazione
    #di tasti Ctrl-C termini in modo pulito tutti i thread generati
    server.daemon_threads = True  
    #il Server acconsente al riutilizzo del socket anche se ancora non è stato
    #rilasciato quello precedente, andandolo a sovrascrivere
    server.allow_reuse_address = True

    #print (workTime()+'Server is up on port: '+str(port)+' (Press Ctrl+C to close server)')

    #Abilitiamo il server a ricevere sempre richieste finchè non viene bloccato
    server.serve_forever()

#Funzione per permetterci di uscire dal processo tramite Ctrl-C
def signal_handler(signal, frame):
    #print( '\nExiting http server (Ctrl+C pressed)')
    try:
      if(server):
        server.server_close()
    finally:
      sys.exit(0)

#Interrompe l’esecuzione se da tastiera arriva la sequenza (CTRL + C)
signal.signal(signal.SIGINT, signal_handler)

run()