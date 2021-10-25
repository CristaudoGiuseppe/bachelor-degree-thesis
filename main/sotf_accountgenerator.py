# -*- coding: utf-8 -*-
#!/bin/env python

''' ACCOUNT GENERATOR SOTF '''

import os, sys, requests, json, random, csv, time, threading, utility, cloudscraper
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from os import system
from threading import Thread, Lock

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + str(exc_value))
    input("Press ENTER to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

os.chdir(os.path.dirname(sys.executable))
configDict = utility.getDictConfig()
delay = float(configDict.get('delay'))
api_key = configDict.get('2captcha')
site_key = '6Lcm-XIUAAAAAMSMGVyiOx_jSYwkq9XyZgyj8pL9'
url = 'https://www.sotf.com/it'
allProxies = None

mutex = Lock()

def GetCaptcha():

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Solving captcha.. '+ utility.bcolors.ENDC)
    logging.info('[ACCOUNT GENERATOR SOTF] Solving captcha..')

    while True:
        try:
            captcha_id = requests.post('http://2captcha.com/in.php?key='+api_key+'&method=userrecaptcha&googlekey='+site_key+'&pageurl='+url)
            captcha_id = captcha_id.text.split('OK|')[1]
            break
        except:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Something went wrong during first captcha solving..'+ utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + ' ['+str(captcha_id.text)+'] Something went wrong during first captcha solving')
            time.sleep(delay)
            continue

    while True:

        try:
            recaptcha_answer = requests.get('http://2captcha.com/res.php?key='+api_key+'&action=get&id='+captcha_id)
            recaptcha_answer = recaptcha_answer.text.split('OK|')[1]
            print(utility.threadTime('') +utility.bcolors.OKGREEN+ 'Finally got captcha token..' +utility.bcolors.ENDC)
            break
        except:
            continue
    
    return recaptcha_answer

def GenerateAccount(session, accountDict, captcha, prx):

    accountPayloud = {
        'from_cart': '',
        'no_reg': '',
        'SendData': '1',
        'Clienti_codice_alternativo': '',
        'is_azienda': '0',
        'Clienti_nome': accountDict['first name'],
        'Clienti_password': accountDict['password'],
        'Clienti_email': accountDict['email'],
        'Clienti_ritenuta_sesso': 'M',
        'Clienti_cognome': accountDict['last name'],
        'Clienti_password2': accountDict['password'],
        'Clienti_ritenuta_datanascita': accountDict['birthday'],
        'gg': accountDict['birthday'].split('/')[0],
        'mm': accountDict['birthday'].split('/')[1],
        'aa': accountDict['birthday'].split('/')[2],
        'g-recaptcha-response': captcha,
        'newsletter': '1',
        'LocationRedirect': 'Search.php',
        'action': 'ins',
        'clienti_ID': '0',
        'Clienti': '',
        'doit': '1',
        'user_track': '0'
    }

    headerCF = dict(session.headers)
    headerCF.update({'origin': 'https://www.sotf.com'})
    headerCF.update({'referer': 'https://www.sotf.com/it/secure/request_account.php'})

    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Generating account with email: ' + accountDict.get('email') + utility.bcolors.ENDC)
    logging.info('[ACCOUNT GENERATOR SOTF] ' + 'Generating account with email: ' + accountDict.get('email'))

    while True:

        try:
            r = session.post('https://www.sotf.com/it/secure/request_account.php', data=accountPayloud, headers=headerCF, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed generating account, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed generating account, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed generating account, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed generating account, retrying..')
            time.sleep(delay)
            continue

        if 'https://www.sotf.com/it/thnx_reg.php' in str(r.url):
            print(utility.threadTime('') + utility.bcolors.OKGREEN + 'Account succesfully generated!' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + 'Account succesfully generated!')
            break
        else:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed generating account, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '['+str(r.status_code)+'] [ERROR] Failed generating account, retrying..')
            time.sleep(delay)
            continue

    return proxy

def GetAddressToken(session, accountDict, prx):

    headerCF = dict(session.headers)
    headerCF.update({'origin': 'https://www.sotf.com'})
    headerCF.update({'referer': 'https://www.sotf.com/it/secure/request_account.php'})

    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Setting address info..' + utility.bcolors.ENDC)
    logging.info('[ACCOUNT GENERATOR SOTF] Setting address info..')

    while True:

        try:
            r = session.get('https://www.sotf.com/it/secure/user_change_data.php', headers=headerCF, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue

            soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting address token, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting address token, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting address token, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting address token, retrying..')
            time.sleep(delay)
            continue

        try:
            clientiID = soup.find('input', {'name':'Clienti_ID'})['value']
            provinceList = BeautifulSoup(str(soup.find('select', {'name':'Province_ID'})), 'html.parser').findAll('option')

            for province in provinceList:
                if str(accountDict['province']).upper() in province.text:
                    return clientiID, province['value'], proxy
            
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting province code, you have to set address manually' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[ERROR] Failed getting province code, you have to set address manually')

            return clientiID, '', proxy

        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR 1] Failed getting address token, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR 1] Failed getting address token, retrying..')
            time.sleep(delay)
            continue

    return clientiID, 'provinceOk', proxy

def SetAddress(session, accountDict, clientiID, province, prx):

    accountPayloud = {
        'SendData': '1',
        'Clienti_codice_alternativo': '',
        'Nazioni_ID': '85',
        'Clienti_nome': accountDict['first name'],
        'Clienti_cognome': accountDict['last name'],
        'Clienti_ritenuta_datanascita': accountDict['birthday'],
        'Clienti_PI': '',
        'Clienti_citta': accountDict['city'],
        'Province_ID': province,
        'Clienti_indirizzo': accountDict['address'],
        'Clienti_numcivico': accountDict['house number'],
        'Clienti_cap': accountDict['zipcode'],
        'Clienti_tel': accountDict['phone number'],
        'Clienti_cell': '',
        'Clienti_fax': '',
        'Clienti_email': accountDict['email'],
        'LocationRedirect': 'Search.php',
        'from_checkout': '',
        'clienti_ID': clientiID,
        'Clienti': '',
        'doit': '1',
        'user_track': '0',
        'reload_naz': '0'
    }

    headerCF = dict(session.headers)
    headerCF.update({'origin': 'https://www.sotf.com'})
    headerCF.update({'referer': 'https://www.sotf.com/it/secure/request_account.php'})

    proxy = prx

    while True:

        try:
            r = session.post('https://www.sotf.com/it/secure/user_change_data.php', data=accountPayloud, headers=headerCF, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed generating account, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed generating account, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed generating account, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed generating account, retrying..')
            time.sleep(delay)
            continue

        if 'https://www.sotf.com/it/login.php' in str(r.url):
            print(utility.threadTime('') + utility.bcolors.OKGREEN + 'Address succesfully added!' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + 'Address succesfully added!')
            break
        else:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding address, retrying..' + utility.bcolors.ENDC)
            logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '['+str(r.status_code)+'] [ERROR] Failed adding address, retrying..')
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
    
    prx = GetNewProxy()

    captcha = GetCaptcha()

    s = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'mobile': False,
            'platform': 'windows'
            #'platform': 'darwin'
        },captcha={'provider':'2captcha','api_key':api_key, 'no_proxy':False},
        doubleDown=False,
        debug=False,
        requestPostHook=utility.injection,
        cipherSuite='EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH'
    )

    s.proxies = prx

    prx = GenerateAccount(s, accountDict, captcha, prx)
    clientiID, province, prx = GetAddressToken(s, accountDict, prx)
    
    if province == '':
        pass
    else:
        SetAddress(s, accountDict, clientiID, province, prx)

    account = open('accounts.txt', 'a')
    account.write('[SOTF] '+accountDict.get('email') + ':'+accountDict.get('password')+'\n')
    account.close()

    input('')
    time.sleep(100)
 
def start_main():

    title = utility.getTitleHeader() + "  - Account generator Sotf"
    utility.setTitle(title)

    try:
        global allProxies
        allProxies = utility.loadProxies('sotf')

        with open('sotf/accounts.csv', 'r') as csv_file:
            
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

                birthday = utility.getBirthday().replace('-','/')

                accountDict = {
                    'email':email,
                    'password':line['PASSWORD'],
                    'first name':name,
                    'last name':line['LAST NAME'],
                    'birthday': birthday,
                    'phone number':phone_number,
                    'address':line['ADDRESS'],
                    'house number': line['HOUSE NUMBER'],
                    'zipcode':line['ZIPCODE'],
                    'city':line['CITY'],
                    'province':line['PROVINCE']
                }

                t = threading.Thread(target=main, args=(accountDict, ''))
                t.start()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[ACCOUNT GENERATOR SOTF] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)
            
if __name__ == '__main__':
    start_main() 