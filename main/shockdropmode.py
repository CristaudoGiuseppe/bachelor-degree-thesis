import os, requests, sys, json, socket, time, threading, itertools, utility, logging
import holypop, hills, susi, awlab, grosbasket, airness, allike, asphaltgold
import cornerstreet, holypop, sotf, sugar, workingclassheroes, revolve
import mytheresa
from os import system

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info(str(traceback.print_exception(exc_type, exc_value, tb)))
    input("Press any key to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

os.chdir(os.path.dirname(sys.executable))

def checkConfig():

    configDict = utility.getDictConfig()

    try:
        awlabMode = configDict.get('awlab_shockdropmode')
        #print(awlabMode)
        allikeMode = configDict.get('allike_shockdropmode')
        #print(allikeMode)
        asphaltMode = configDict.get('asphaltgold_shockdropmode')
        #print(asphaltMode)
        wchMode = configDict.get('wch_shockdropmode')
        #print(wchMode)
        revolveMode = configDict.get('revolve_shockdropmode')
        #print(revolveMode)

        if awlabMode == "" or allikeMode == "" or asphaltMode == "" or wchMode == "" or revolveMode == "":
            print(utility.bcolors.FAIL + "\tFailed getting mode, check your config file.." + utility.bcolors.ENDC)
            logging.info("Failed getting mode, check your config file..")
            input('\tPress ENTER to exit.')
            sys.exit()
        else:
            pass

    except:
        print(utility.bcolors.FAIL + "\tFailed getting mode, check your config file.." + utility.bcolors.ENDC)
        logging.info("Failed getting mode, check your config file..")
        input('\tPress ENTER to exit.')
        sys.exit()

    
    try:
        nTask = configDict.get('shockdropmodetasks')
        val = int(nTask)

        if val == 0 or val < 0:
            print(utility.bcolors.FAIL + "\tImpossible to start 0 or < task, check your config file.." + utility.bcolors.ENDC)
            logging.info("Impossible to start 0 or < task, check your config file..")
            input('\tPress ENTER to exit.')
            sys.exit()
        else:
            pass

    except ValueError as e:
        print(utility.bcolors.FAIL + "\tFailed loading task number, check your config file.." + utility.bcolors.ENDC)
        logging.info("Failed loading task number, check your config file.." + str(e))
        input('\tPress ENTER to exit.')
        sys.exit()


    return awlabMode, allikeMode, asphaltMode, wchMode, revolveMode, val

def start_main():
    title = utility.getTitleHeader() + "  -  Shockdrop Mode"
    utility.setTitle(title)

    utility.printLogo()

    print(utility.bcolors.HEADER+' Shockdrop Mode\n'+utility.bcolors.ENDC)
    awM, allikeM, asphaltM, wchM, revM, val = checkConfig()

    URL = input('Insert URL to start tasks > ')
    logging.info(URL)

    utility.clearCLI()

    if('www.aw-lab' in URL or 'AW_' in URL or 'es.aw-lab' in URL or 'en.aw-lab' in URL):
        awlab.shockdrop(URL, val, awM)
    elif('www.cornerstreet' in URL): 
        cornerstreet.shockdrop(URL, val)
    elif('www.susi' in URL):
        susi.shockdrop(URL, val)
    elif('https://airness' in URL or 'www.airness' in URL):
        airness.shockdrop(URL, val)
    elif('www.7hillsroma' in URL):
        hills.shockdrop(URL, val)
    elif('www.grosbasket' in URL):
        grosbasket.shockdrop(URL, val)
    elif('www.allike' in URL):
        allike.shockdrop(URL, val, allikeM)
    elif('www.asphaltgold' in URL):
        asphaltgold.shockdrop(URL, val, asphaltM)
    elif('www.sotf' in URL):
        sotf.shockdrop(URL, val)
    elif('www.sugar' in URL):
        sugar.shockdrop(URL, val)
    elif('www.workingclassheroes' in URL):
        workingclassheroes.shockdrop(URL, val, wchM)
    elif('www.revolve' in URL):
        revolve.shockdrop(URL, val, revM)
    elif('www.mytheresa' in URL):
        mytheresa.shockdrop(URL, val)
    elif('www.holypopstore' in URL or utility.hasNumbers(URL)):
        holypop.shockdrop(URL, val)
    else:
        utility.printLogo()
        print(utility.bcolors.HEADER+' Shockdrop mode\n'+utility.bcolors.ENDC)
        print(utility.bcolors.WARNING+ '\tURL not recognized, restarting..' +utility.bcolors.ENDC)
        logging.info('[SHOCKDROP] URL not recognized, restarting..')
        time.sleep(2)
        start_main()
 
if __name__ == '__main__':
    start_main() 