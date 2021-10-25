import os, requests, sys, json, socket, time, threading, itertools
import holypop, hills, susi, awlab, grosbasket, shockdropmode, airness, allike, workingclassheroes, asphaltgold, cornerstreet, sotf, sugar, revolve, mytheresa, unieuro
import address, crissWebhook
import holypop_accountgenerator, sugar_accountgenerator, sotf_accountgenerator
from pypresence import Presence
from datetime import datetime
from os import system
from bs4 import BeautifulSoup
import logging, utility
import autoupdater

mainTitle = utility.getTitleHeader()
version = utility.getVersion()
utility.setTitle(mainTitle)

client_id = "713506064649158741"  # Enter your Application ID here.
RPC = Presence(client_id=client_id)

logging.basicConfig(filename='debug.log',level=logging.INFO)

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    #traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[MAIN] ' + str(traceback.print_exception(exc_type, exc_value, tb)))
    input("Press ENTER to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit
os.chdir(os.path.dirname(sys.executable))

try:

    def startDiscordPresence():
        global RPC

        try:
            RPC.connect()

            # current date and time
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            # Make sure you are using the same name that you used when uploading the image
            RPC.update(large_image="crissaio_logo", small_image='purple_ball', state='Version '+version, details='Idle', start=timestamp) #state=''
        except Exception as e:
            logging.info('[DISCORD PRESENCE] ' + str(e))
            pass
        
    def updateDiscordPresence(website):
        global RPC

        try:
            # current date and time
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            # Make sure you are using the same name that you used when uploading the image
            RPC.update(large_image="crissaio_logo", small_image='purple_ball', state='Version '+version, details=website, start=timestamp) #state=''
        except Exception as e:
            logging.info('[DISCORD PRESENCE] ' + str(e))
            pass

    def activate():

        utility.printLogo()

        configDict = utility.getDictConfig()
        key = configDict.get('key')

        if(key == ''):
            print(utility.bcolors.OKGREEN + ' Enter license key' + utility.bcolors.ENDC)
            logging.info('[MAIN] Enter license key')
            key = input(utility.bcolors.OKGREEN + ' > ' + utility.bcolors.ENDC)

            with open('config.json', 'r') as configFile:  # reading JSON object
                data = json.load(configFile)
                data['key'] = key
                configFile.close()

            with open('config.json', 'w+') as configFile:  # writing JSON object
                configFile.write(json.dumps(data))
                configFile.close()

            utility.printLogo()

        print(utility.bcolors.OKGREEN + '   Activating key ['+key+']' + utility.bcolors.ENDC)
        logging.info('[MAIN] Activating key')

        ## getting the hostname by socket.gethostname() method
        
        hostname = socket.gethostname()
        
        try:
            ip_address = requests.get('https://api.ipify.org/').text
            #print(ip_address)
        except Exception as e:
            utility.printLogo()
            print(utility.bcolors.FAIL + '   DETECTED NOT ALLOWED SOFTWARE!' + utility.bcolors.ENDC)
            logging.info('DETECTED NOT ALLOWED SOFTWARE\nReason: '+str(e))
            #crissWebhook.CrackAttemptWebhook('DETECTED NOT ALLOWED SOFTWARE')
            time.sleep(20)
            sys.exit()

        #TRE TYPE OF IP!

        #ip_address = socket.gethostbyname(hostname)

        #ip_address = socket.getfqdn())

        #print([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
        
        payload = {
            'key':key,
            'hostname':hostname,
            'ip':ip_address
        }

        try:
            r = requests.get('http://95.179.183.203:5000/', params=payload, timeout=30) #95.179.183.203
        except Exception as e:
            utility.printLogo()
            print(utility.bcolors.FAIL + "   Probably CrissAIO's server offline " + utility.bcolors.ENDC)
            logging.info('[MAIN] Probably CrissAIO server offline')
            logging.info('[MAIN] ' + str(e))
            #time.sleep(100)
            input('Press ENTER to exit.')
            sys.exit()

        if r.status_code == 504:
            utility.printLogo()
            print(utility.bcolors.FAIL + '   Key already binded to another computer, reset it on Discord' + utility.bcolors.ENDC)
            logging.info('[MAIN] ' + '[' + str(r.status_code) + ']' + ' Key already binded to another computer, reset it on Discord')
            input('Press ENTER to exit.')
            #time.sleep(100)
            sys.exit()
        if r.status_code == 503:
            utility.printLogo()
            print(utility.bcolors.FAIL + '   This key need to be binded on Discord!' + utility.bcolors.ENDC)
            logging.info('[MAIN] ' + '[' + str(r.status_code) + ']' + ' This key need to be binded on Discord!')
            input('Press ENTER to exit.')
            #time.sleep(100)
            sys.exit()
        if r.status_code == 200:
            utility.printLogo()
            print(utility.bcolors.OKGREEN + '   Key succesfully binded to this computer' + utility.bcolors.ENDC)
            logging.info('[MAIN] ' + '[' + str(r.status_code) + ']' + ' Key succesfully binded to this computer')
            time.sleep(1)
            startBot(key)
        if r.status_code == 201:
            utility.printLogo()
            print(utility.bcolors.OKGREEN + '   Valid key!' + utility.bcolors.ENDC)
            logging.info('[MAIN] ' + '[' + str(r.status_code) + ']' + ' Valid key!')
            time.sleep(1)
            startBot(key)
        if r.status_code == 404:
            utility.printLogo()
            print(utility.bcolors.FAIL +'   Key not found in our server!' + utility.bcolors.ENDC)
            logging.info('[MAIN] ' + '[' + str(r.status_code) + ']' + ' Key not found in our server!')
            input('Press ENTER to exit.')
            #time.sleep(100)
            sys.exit()
        if r.status_code == 500:
            utility.printLogo()
            print(utility.bcolors.FAIL +'   Something went wrong...' + utility.bcolors.ENDC)
            logging.info('[MAIN] ' + '[' + str(r.status_code) + ']' + ' Something went wrong...')
            input('Press ENTER to exit.')
            #time.sleep(100)
            sys.exit()

    def startBot(key):
        
        startDiscordPresence()
        utility.printLogo()
        
        print (' Version: '+utility.bcolors.HEADER+version+utility.bcolors.ENDC+' | Key: '+utility.bcolors.HEADER+key+utility.bcolors.ENDC+'\n')

        print (utility.bcolors.HEADER+' X '+utility.bcolors.ENDC+'Shockdrop Mode'+utility.bcolors.HEADER+'\t Y '+utility.bcolors.ENDC+'Account Generator\n')
        print (utility.bcolors.HEADER+' 1 '+utility.bcolors.ENDC+'Holypop'+utility.bcolors.HEADER+'\t 6 '+utility.bcolors.ENDC+' Airness'+utility.bcolors.HEADER+'\t\t 11 '+utility.bcolors.ENDC+'Sotf')
        print (utility.bcolors.HEADER+' 2 '+utility.bcolors.ENDC+'7Hills'+utility.bcolors.HEADER+'\t 7 '+utility.bcolors.ENDC+' Allike'+utility.bcolors.HEADER+'\t\t 12 '+utility.bcolors.ENDC+'Sugar')
        print (utility.bcolors.HEADER+' 3 '+utility.bcolors.ENDC+'Susi'+utility.bcolors.HEADER+'\t\t 8 '+utility.bcolors.ENDC+' WorkingClassHeroes'+utility.bcolors.HEADER+'\t 13 '+utility.bcolors.ENDC+'Revolve')
        print (utility.bcolors.HEADER+' 4 '+utility.bcolors.ENDC+'AWLAB'+utility.bcolors.HEADER+'\t 9 '+utility.bcolors.ENDC+' Ashpalt Gold'+utility.bcolors.HEADER+'\t 14 '+utility.bcolors.ENDC+'Mytheresa')
        print (utility.bcolors.HEADER+' 5 '+utility.bcolors.ENDC+'Grosbasket'+utility.bcolors.HEADER+'\t 10 '+utility.bcolors.ENDC+'Cornerstreet'+utility.bcolors.HEADER+'\t 15 '+utility.bcolors.ENDC+'Unieuro\n')
        
        site = input('> ')

        utility.clearCLI()

        if site == '1':
            updateDiscordPresence('Holypop')
            holypop.start_main()
        elif site == '2':
            updateDiscordPresence('Hills')
            hills.start_main()
        elif site == '3':
            updateDiscordPresence('Susi')
            susi.start_main()
        elif site == '4':
            updateDiscordPresence('AW-LAB')
            awlab.start_main()
        elif site == '5':
            updateDiscordPresence('Grosbasket')
            grosbasket.start_main()
        elif site == '6':
            updateDiscordPresence('Airness')
            airness.start_main()
        elif site == '7':
            updateDiscordPresence('Allike')
            allike.start_main()
        elif site == '8':
            updateDiscordPresence('WCH')
            workingclassheroes.start_main()
        elif site == '9':
            updateDiscordPresence('Asphaltgold')
            asphaltgold.start_main()
        elif site == '10':
            updateDiscordPresence('Cornerstreet')
            cornerstreet.start_main()
        elif site == '11':
            updateDiscordPresence('Sotf')
            sotf.start_main()
        elif site == '12':
            updateDiscordPresence('Sugar')
            sugar.start_main()
        elif site == '13':
            updateDiscordPresence('Revolve')
            revolve.start_main()
        elif site == '14':
            updateDiscordPresence('Mytheresa')
            mytheresa.start_main()
        elif site == '15':
            updateDiscordPresence('Unieuro')
            unieuro.start_main()
        elif site.upper() == 'X':
            updateDiscordPresence('Shockdrop')
            utility.printLogo()
            utility.clearCLI()
            shockdropmode.start_main()
        elif site.upper() == 'Y':
            while True:
                utility.printLogo()
                print(utility.bcolors.HEADER + ' Account Generator\n' + utility.bcolors.ENDC)
                print(utility.bcolors.HEADER + ' X ' + utility.bcolors.ENDC +'Exit\n')
                print (utility.bcolors.HEADER+' 1 '+utility.bcolors.ENDC+'[Sugar]   - Account Generator')
                print (utility.bcolors.HEADER+' 2 '+utility.bcolors.ENDC+'[Sotf]    - Account Generator')
                print (utility.bcolors.HEADER+' 3 '+utility.bcolors.ENDC+'[Holypop] - Account Generator')
                print (utility.bcolors.HEADER+' 4 '+utility.bcolors.ENDC+'[Holypop] - Set Address\n')
                site = input('> ')
                utility.clearCLI()
                if site == '1':
                    sugar_accountgenerator.start_main()
                    break
                elif site == '2':
                    sotf_accountgenerator.start_main()
                    break
                elif site == '3':
                    holypop_accountgenerator.start_main()
                    break
                elif site == '4':
                    address.start_main()
                    break
                elif site == 'X':
                    startBot(key)
                    break
                else:
                    continue
        else:
            startBot(key)

    client = autoupdater.Client()
    activate()

except KeyboardInterrupt as e:
    logging.info('[MAIN] ' + str(e))
    input("Press ENTER to exit.")
    sys.exit()