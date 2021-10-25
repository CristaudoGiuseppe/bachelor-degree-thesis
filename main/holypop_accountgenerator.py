# -*- coding: utf-8 -*-
#!/bin/env python

''' ACCOUNT GENERATOR HOLYPOP '''

import os, sys, requests, json, random, csv, threading, time, utility
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from threading import Thread, Lock
from os import system

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[ACCOUNT GENERATOR HOLYPOP] ' + utility.threadTime('') + str(exc_value))
    input("Press ENTER to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

os.chdir(os.path.dirname(sys.executable))
configDict = utility.getDictConfig()
delay = float(configDict.get('delay'))
allProxies = None
mutex = Lock()

headersXML = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

def generateAccount(session, accountDict, prx):

    proxy = prx

    birthDate = utility.getBirthdayHoly()

    accountPayload = {
        'controller': 'auth',
        'action': 'register',
        'extension': 'holypop',
        'email': accountDict.get('email'),
        'password': accountDict.get('password'),
        'firstName': accountDict.get('name'),
        'lastName': accountDict.get('last name'),
        'birthDate': birthDate,
        'sex': 'MALE',
        'privacy[1]': '1',
        'privacy[2]': '0',
        'redirectTo': 'https://www.holypopstore.com/en/account',
        'language': 'EN',
        'version': '291',
        'cookieVersion': '291'
    }

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Generating account with email: ' + accountDict.get('email') + utility.bcolors.ENDC)
    logging.info('[ACCOUNT GENERATOR HOLYPOP] ' + 'Generating account with email: ' + accountDict.get('email'))

    while True:

        try:
            r = session.post('https://www.holypopstore.com/index.php', headers=headersXML, data=accountPayload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ACCOUNT GENERATOR HOLYPOP] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                #proxy = getNewProxy()
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR HOLYPOP] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            #proxy = getNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR HOLYPOP] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            #proxy = getNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed generating account, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR HOLYPOP] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed generating account, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed generating account, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR HOLYPOP] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed generating account, retrying..')
            time.sleep(delay)
            continue

        try:
            jsonSuccess = json.loads(r.text)
            if jsonSuccess['success']:
                print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully created account!' +utility.bcolors.ENDC)
                logging.info('[ACCOUNT GENERATOR HOLYPOP] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully created account!')
                return True
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[' + str(jsonSuccess['error']['message'])+ '] Failed generating account!' + utility.bcolors.ENDC)
                logging.info('[ACCOUNT GENERATOR HOLYPOP] ' + utility.threadTime('') + '[' + str(jsonSuccess['error']['message']) + '] ['+str(jsonSuccess['error']['code']) + '] Failed generating account!')
                time.sleep(delay)
                return False
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed generating account, retrying..'  + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR HOLYPOP] ' + utility.threadTime('') + '[' + str(e) + '] Failed generating account, retrying.. ')
            time.sleep(delay)
            continue

def GetNewProxy():
    global mutex
    global allProxies

    mutex.acquire()

    if len(allProxies) != 0:
        index = random.randrange(len(allProxies))
        newProxy = allProxies[index]
        allProxies.remove(newProxy)
    else:
        newProxy = None

    mutex.release()

    return newProxy

def main(accountDict, tmp):
    
    #prx = getNewProxy()
    prx = None
    account = open('accounts.txt', 'a')

    s = requests.session()

    result = generateAccount(s, accountDict, prx)

    if result:
        account.write('[HOLYPOP] '+accountDict.get('email') + ':'+accountDict.get('password')+'\n')
    else:
        pass

    account.close()

    input('')
    time.sleep(100)
 
def start_main():

    title = utility.getTitleHeader() + "  - Account generator Holypop"
    utility.setTitle(title)

    try:
        global allProxies
        allProxies = utility.loadProxies('holypop')
        with open('holypop/accounts.csv', 'r') as csv_file:
            
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:
                
                if('RANDOM' in line['EMAIL']):
                    name, email = utility.getCathcallEMail(line['LAST NAME'], line['EMAIL'].replace('RANDOM', ''))
                else:
                    name = utility.getName()
                    email = line['EMAIL']

                accountDict = {}

                accountDict = {
                    'email':email,
                    'name':name,
                    'last name':line['LAST NAME'],
                    'password':line['PASSWORD']
                }

                t = threading.Thread(target=main, args=(accountDict, ''))
                t.start()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[ACCOUNT GENERATOR HOLYPOP] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)
            
if __name__ == '__main__':
    start_main() 