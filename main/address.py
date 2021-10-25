# -*- coding: utf-8 -*-
#!/bin/env python

''' ADDRESS - HOLYPOP '''

import os, sys, requests, json, random, csv, threading, time, utility
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from os import system

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + str(exc_value))
    input("Press ENTER to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

os.chdir(os.path.dirname(sys.executable))
configDict = utility.getDictConfig()
delay = float(configDict.get('delay'))
all_proxies = None
proxy = None

headersXML = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}

def Login(session, email, password):
    
    login_payload = {
        'controller': 'auth',
        'action': 'authenticate',
        'type': 'standard',
        'extension': 'holypop',
        'credential': email,
        'password': password,
        'language': 'EN',
        'version': 294,
        'cookieVersion': 294
    }

    print(utility.threadTime('') + utility.bcolors.WARNING + ' Logging in: ' + email + '..' + utility.bcolors.ENDC)
    logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + 'Logging in: ' + email + '..')

    while True:

        try:
            r = session.post('https://www.holypopstore.com/index.php', headers=headersXML, allow_redirects=True, data=login_payload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..')
                logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                loadProxies()
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..')
            logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            loadProxies()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..')
            logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            loadProxies()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed loggin in, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed loggin in, retrying..')
            time.sleep(delay)
            continue

        try:
            loginJson = json.loads(r.text)

            if loginJson['success']:
                print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully logged in!' + utility.bcolors.ENDC)
                logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully logged in!')
                break
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[' +str(loginJson['error']['message']) + 'Failed loggin in, retrying..'+ utility.bcolors.ENDC)
                logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(loginJson['error']['message']) + '] ['+str(loginJson['error']['code'])+'] Failed loggin in, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL +'Failed loggin in, account blacklisted!'+ utility.bcolors.ENDC)
            logging.info('[ADDRESS_SETTER] ['+str(e)+'] Failed loggin in, account blacklisted!')
            break

def setAddress(session, accountDict):

    set_address_payload = {
        'controller': 'users',
        'action': 'saveAddresses',
        'addresses[0][counter]': 'nn1',
        'addresses[0][first_name]': accountDict.get('name'),
        'addresses[0][last_name]': accountDict.get('last name'),
        'addresses[0][full_name]': accountDict.get('name')+' '+accountDict.get('last name'),
        'addresses[0][email]': accountDict.get('email'),
        'addresses[0][street_address]': accountDict.get('address'),
        'addresses[0][zipcode]': accountDict.get('zipcode'),
        'addresses[0][cityName]': accountDict.get('city'),
        'addresses[0][statecode]': accountDict.get('state'),
        'addresses[0][stateId]': accountDict.get('state id'),
        'addresses[0][countryId]': 110,
        'addresses[0][countryName]': 'Italia',
        'addresses[0][phone_number]': accountDict.get('phone number'),
        'addresses[0][isDefault]': '1',
        'extension': 'holypop',
        'language': 'EN',
        'version': 294,
        'cookieVersion': 294
    }

    print(utility.threadTime('') +  utility.bcolors.WARNING + 'Setting address..' + utility.bcolors.ENDC)
    logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + 'Setting address..')

    while True:

        try:
            r = session.post('https://www.holypopstore.com/index.php', headers=headersXML, data=set_address_payload, prxoies=proxy)
        
            if r.status_code == 503:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..')
                logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                loadProxies()
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..')
            logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            loadProxies()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..')
            logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            loadProxies()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed setting address, retrying..' + utility.bcolors.ENDC)
            logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed setting address, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed setting address, retrying..' + utility.bcolors.ENDC)
            logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed setting address, retrying..')
            time.sleep(delay)
            continue

        try:
            jsonSuccess = json.loads(r.text)
            
            if jsonSuccess['success']:
                print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully set address!' +utility.bcolors.ENDC)
                logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully set address!')
                break
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+jsonSuccess['error']['message']+'] Failed setting address!' +utility.bcolors.ENDC)
                logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(jsonSuccess['error']['message']) + '] ['+str(jsonSuccess['error']['code']) + '] Failed setting address!')
                break

        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + ' Failed setting address, retrying..' + utility.bcolors.ENDC)
            logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(e) + '] Failed setting address, retrying..')
            time.sleep(delay)
            continue

def loadProxies():
    global all_proxies

    with open('holypop/proxies.txt', 'r') as proxies_file:
        all_proxies = proxies_file.read().split('\n')

    if all_proxies == ['']:
        print('['+str(datetime.now()).split(' ')[1]+'] [STATUS] ' + utility.bcolors.WARNING + 'No proxies found, running localhost..' + utility.bcolors.ENDC)
        logging.info('[ADDRESS SETTER HOLYPOP] No proxies found, running localhost..')
    else:
        print('['+str(datetime.now()).split(' ')[1]+'] [STATUS] ' + utility.bcolors.WARNING + 'Loaded all proxies.' + utility.bcolors.ENDC)
        logging.info('[ADDRESS SETTER HOLYPOP] Loaded all proxies.')

def getProxy():
    global proxy
    proxy_raw = random.choice(all_proxies)

    try:
        proxy_parts = proxy_raw.split(':')
        ip, port, user, password = proxy_parts[0], proxy_parts[1], proxy_parts[2], proxy_parts[3]
        new_proxy = {
            'http': f'http://{user}:{password}@{ip}:{port}',
            'https': f'https://{user}:{password}@{ip}:{port}'
        }
        proxy = new_proxy
    except:
        logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + 'Failed getting proxy..')
        pass

def main(tmp, accountDict):

    getProxy()

    s = requests.session()

    Login(s, accountDict.get('email'), accountDict.get('password'))
    setAddress(s, accountDict)

def start_main():

    title = utility.getTitleHeader() + "  - Address setter Holypop"
    utility.setTitle(title)
    
    try:
        loadProxies()
        with open('holypop/address.csv', 'r') as csv_file:
            
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:
                
                accountDict = {}

                name = line['FIRST NAME']
                email = line['EMAIL']

                if('RANDOM' not in email) and ('RANDOM' in name):
                    name = utility.getName()

                phone_number = line['PHONE']
                if('RANDOM' in phone_number):
                    phone_number = utility.getRandomNumber()

                accountDict = {
                    'email':email,
                    'password':line['PASSWORD'],
                    'name':name,
                    'last name':line['LAST NAME'],
                    'phone number':phone_number,
                    'address':line['ADDRESS'],
                    'zipcode':line['ZIPCODE'],
                    'state':line['PROVINCE'],
                    'city':line['CITY'],
                    'state id':line['STATE ID']
                }

                t = threading.Thread(target=main, args=('', accountDict))
                t.start()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[ADDRESS SETTER HOLYPOP] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)
            
if __name__ == '__main__':
    start_main() 