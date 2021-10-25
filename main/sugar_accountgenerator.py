# -*- coding: utf-8 -*-
#!/bin/env python

''' ACCOUNT GENERATOR SUGAR '''

import os, sys, requests, json, random, csv, time, threading, utility
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from os import system
from threading import Thread, Lock

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + str(exc_value))
    input("Press ENTER to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

os.chdir(os.path.dirname(sys.executable))
configDict = utility.getDictConfig()
delay = float(configDict.get('delay'))
allProxies = None

mutex = Lock()

def GettingToken(session, prx):

    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Getting token.. '+ utility.bcolors.ENDC)
    logging.info('[ACCOUNT GENERATOR SUGAR] ' + 'Getting token..')

    while True:

        try:
            r = session.get('https://www.sugar.it/customer/account/create/', proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..'+ utility.bcolors.ENDC)
                logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..'+ utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..'+ utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting token, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting token, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting token, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting token, retrying..')
            time.sleep(delay)
            continue

        try:
            form_key = BeautifulSoup(r.text, 'html.parser').find('input', {'name':'form_key'})['value']
            print(utility.threadTime('') + utility.bcolors.OKGREEN + 'Succesfully got token!' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + 'Succesfully got token!')
            break
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting token, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting token, retrying..')
            time.sleep(delay)
            continue

    return form_key, proxy

def GenerateAccount(session, accountDict, form_key, prx):

    accountPayloud = {
        'form_key': form_key,
        'success_url': '',
        'error_url': '',
        'firstname': accountDict['first name'],
        'lastname': accountDict['last name'],
        'gender': '1',
        'email': accountDict['email'],
        'password': accountDict['password'],
        'password_confirmation': accountDict['password']
    }

    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Generating account with email: ' + accountDict.get('email') + utility.bcolors.ENDC)
    logging.info('[ACCOUNT GENERATOR SUGAR] ' + 'Generating account with email: ' + accountDict.get('email'))

    while True:

        try:
            r = session.post('https://www.sugar.it/customer/account/createpost/', data=accountPayloud, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..'+ utility.bcolors.ENDC)
                logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..'+ utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..'+ utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed generating account, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed generating account, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed generating account, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed generating account, retrying..')
            time.sleep(delay)
            continue

        try:
            check = BeautifulSoup(r.text, 'html.parser').find('div', {'class':'block-title'})
            print(utility.threadTime('') + utility.bcolors.OKGREEN + 'Account succesfully generated!' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + 'Account succesfully generated!')
            break
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed generating account, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed generating account, retrying..')
            time.sleep(delay)
            continue

        return proxy

def SetAddress(session, accountDict, prx):

    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Setting address..'+utility.bcolors.ENDC)
    logging.info('[ACCOUNT GENERATOR SUGAR] ' + 'Setting address..')

    while True:
    
        try:
            r = session.get('https://www.sugar.it/customer/address/edit/', proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..'+ utility.bcolors.ENDC)
                logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..'+ utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..'+ utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed setting address, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed setting address, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed setting address, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed setting address, retrying..')
            time.sleep(delay)
            continue

        try:
            form_key = BeautifulSoup(r.text, 'html.parser').find('input', {'name':'form_key'})['value']
            break
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting address token, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting addres  token, retrying..')
            time.sleep(delay)
            continue

    accountPayloud = {
        'form_key': form_key,
        'success_url': '',
        'error_url': '',
        'firstname': accountDict['first name'],
        'lastname': accountDict['last name'],
        'company': '',
        'telephone': accountDict['phone_number'],
        'street[]': accountDict['address'],
        'city': accountDict['city'],
        'region': '',
        'postcode': accountDict['zipcode'],
        'country_id': accountDict['country_id'],
        'default_billing': 1,
        'default_shipping': 1
    }

    while True:

        try:
            r = session.post('https://www.sugar.it/customer/address/formPost/', data=accountPayloud, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..')
                logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..')
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..')
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed setting address, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed setting address, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed setting address, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed setting address, retrying..')
            time.sleep(delay)
            continue

        try:
            check = BeautifulSoup(r.text, 'html.parser').find('a', {'class':'action edit'})
            print(utility.threadTime('') + utility.bcolors.OKGREEN + 'Address succesfully set!' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + 'Address succesfully set!')
            break
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed setting address, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed setting address, retrying..')
            time.sleep(delay)
            continue

        return proxy

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
    
    prx = GetNewProxy()

    s = requests.session()

    form_key, prx = GettingToken(s, prx)
    prx = GenerateAccount(s, accountDict, form_key, prx)
    SetAddress(s, accountDict, prx)

    account = open('accounts.txt', 'a')
    account.write('[SUGAR] '+accountDict.get('email') + ':'+accountDict.get('password')+'\n')
    account.close()

    input('')
    time.sleep(100)
 
def start_main():

    title = utility.getTitleHeader() + "  - Account generator Sugar"
    utility.setTitle(title)

    try:
        global allProxies
        allProxies = utility.loadProxies('sugar')

        with open('sugar/accounts.csv', 'r') as csv_file:
            
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:
                
                if('RANDOM' in line['EMAIL']):
                    name, email = utility.getCathcallEMail(line['LAST NAME'], line['EMAIL'].replace('RANDOM', ''))
                else:
                    name = utility.getName()
                    email = line['EMAIL']

                phone_number = line['PHONE']
                if('RANDOM' in phone_number):
                    phone_number = utility.getRandomNumber()

                accountDict = {
                    'email':email,
                    'password':line['PASSWORD'],
                    'first name':name,
                    'last name':line['LAST NAME'],
                    'phone_number':phone_number,
                    'address':line['ADDRESS'],
                    'zipcode':line['ZIPCODE'],
                    'city':line['CITY'],
                    'country_id':line['COUNTRY']
                }

                t = threading.Thread(target=main, args=(accountDict, ''))
                t.start()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[ACCOUNT GENERATOR SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)
            
if __name__ == '__main__':
    start_main() 