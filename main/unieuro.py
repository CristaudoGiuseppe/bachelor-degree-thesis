# -*- coding: utf-8 -*-
#!/bin/env python

''' UNIEURO '''

import requests, signal, json, random, csv, time, sys, re, os, utility, crissWebhook, base64
from bs4 import BeautifulSoup
from datetime import datetime, date
import logging
from threading import Thread, Lock
from os import system

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[UNIEURO] ' + utility.threadTime(payment) + str(exc_value))
    input("Press ENTER to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

os.chdir(os.path.dirname(sys.executable))
configDict = utility.getDictConfig()
delay = float(configDict.get('delay'))
allProxies = None

mutex = Lock()

counterTitle = int(0)
carted = int(0)
checkouted = int(0)

def setTitle(mode):
      
    global mutex
    global counterTitle
    global carted
    global checkouted

    mutex.acquire()
    if counterTitle == 0:
        counterTitle = 1
        if mode == 0:
            carted = carted + 1
        else:
            checkouted = checkouted + 1
    else:
        if mode == 0:
            carted = carted + 1
        else:
            checkouted = checkouted + 1
    

    title = utility.getTitleHeader() + "  -  Unieuro  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()

def ProductScraper(session, payment, url, prx):

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
    logging.info('[UNIEURO] ' + utility.threadTime(payment) + 'Getting product info..')

    while True:

        try:
            r = session.get(url, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        

        try:
            ''' SKU '''
            sku = soup.find('div', {'data-module':'productdetail'})['data-productdetail-sku']

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [SKU] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] [SKU] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

        try:

            if 'Aggiungi al carrello' in soup.find('a', {'data-sku':sku}).text:
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Product available!' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Product available!')
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[' + str(r.status_code) + '] Product not available, retrying..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Product not available, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed available check, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed available check, retrying..')
            time.sleep(delay)
            continue
    
    return sku, proxy

def AddToCart(session, payment, sku, prx):
    
    atc_payload = {
        'productCode': sku
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.unieuro.it',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    proxy = prx

    while True:

        try:

            r = session.post('https://www.unieuro.it/online/precart/add', headers=headers, data=atc_payload, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        
        try:
            jsonATC = json.loads(r.text)
            if '1' in str(jsonATC['cartData']['total_quantity']):
                productURL = 'https://www.unieuro.it/online' + jsonATC['cartData']['products'][0]['url']
                productTitle = jsonATC['cartData']['products'][0]['title']
                productImage = 'https://static1.unieuro.it' + jsonATC['cartData']['products'][0]['image']
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully added to cart!')
                setTitle(0)
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(jsonATC['cartData']['total_price'])+'] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[ERROR] ['+str(jsonATC['cartData']['total_price'])+'] [' + str(r.status_code) + '] Failed adding to cart, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        
    return productURL, productTitle, productImage, proxy

def SetAccount(session, payment, accountDict, prx):

    account_payload = {
        'registerForm.firstName': accountDict['first_name'],
        'registerForm.lastName': accountDict['last_name'],
        'registerForm.email': accountDict['email'],
        'registerForm.pwd': accountDict['password'],
        'registerForm.checkPwd': accountDict['password'],
        'registerForm.phone': accountDict['phone_number'],
        'registerForm.flagPrivacy': 'true',
        'registerForm.flagNewsletter': 'false',
        'registerForm.flagProfilation': 'false',
        'registerForm.flagCessionThirdPart': 'false',
        'flagRegistration': 'true'
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.unieuro.it',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Setting account info..' + utility.bcolors.ENDC)
    logging.info('[UNIEURO] ' + utility.threadTime(payment) + 'Setting account info..')

    while True:

        try:

            r = session.post('https://www.unieuro.it/online/checkout/delivery/validateRegisterData', headers=headers, data=account_payload, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting account info, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed setting account info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting account info, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed setting account info, retrying..')
            time.sleep(delay)
            continue
        
        try:
            jsonATC = json.loads(r.text)
            if jsonATC['save']:
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully set account info!' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully set account info!')
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(jsonATC['errors'][0])+'] Failed setting account info, retrying..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[ERROR] ['+str(jsonATC['errors'][0])+'] [' + str(r.status_code) + '] Failed setting account info, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [' + str(r.status_code) + '] Failed setting account info, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] [' + str(r.status_code) + '] Failed setting account info, retrying..')
            time.sleep(delay)
            continue
        
    return proxy

def SetStore(session, payment, storeID, prx):
    
    store_payload = {
        'store': storeID
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.unieuro.it',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Setting store info..' + utility.bcolors.ENDC)
    logging.info('[UNIEURO] ' + utility.threadTime(payment) + 'Setting store info..')

    while True:
    
        try:
            r = session.get('https://www.unieuro.it/online/cart/changeDeliveryMode?type=store&changingDeliveryMode=true', headers=headers, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting store, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed setting store, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [JSON] Failed setting store, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] [JSON] Failed setting store, retrying..')
            time.sleep(delay)
            continue

        try:
            check = json.loads(r.text)
            break
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [JSON] [' + str(r.status_code) + '] Failed setting store, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] [JSON] [' + str(r.status_code) + '] Failed setting store, retrying..')
            time.sleep(delay)
            continue

    while True:

        try:
            r = session.post('https://www.unieuro.it/online/precart/setstore', headers=headers, data=store_payload, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting store, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed setting store, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting store, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed setting store, retrying..')
            time.sleep(delay)
            continue
        
        try:
            jsonATC = json.loads(r.text)
            if jsonATC['result']:
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Store succesfully set!' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Store succesfully set!')
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(jsonATC['errors'][0])+'] Failed setting store, retrying..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[ERROR] ['+str(jsonATC['errors'][0])+'] [' + str(r.status_code) + '] Failed setting store, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [' + str(r.status_code) + '] Failed setting store, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] [' + str(r.status_code) + '] Failed setting store, retrying..')
            time.sleep(delay)
            continue
        
    return proxy

def SetAddress(session, payment, accountDict, prx):
    
    address_payload = {
        'shippingAddress.firstName': accountDict['first_name'],
        'shippingAddress.lastName': accountDict['last_name'],
        'shippingAddress.phone': accountDict['phone_number'],
        'shippingAddress.town': accountDict['city'],
        'shippingAddress.streetName': accountDict['address'],
        'shippingAddress.streetNumber': accountDict['house_number'],
        'shippingAddress.district': accountDict['province'],
        'shippingAddress.postalCode': accountDict['zipcode'],
        'shippingAddress.notes': '',
        'newShipping': 'true'
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.unieuro.it',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Setting address info..' + utility.bcolors.ENDC)
    logging.info('[UNIEURO] ' + utility.threadTime(payment) + 'Setting address info..')

    while True:

        try:

            r = session.post('https://www.unieuro.it/online/checkout/delivery/validateShippingData', headers=headers, data=address_payload, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting shipping info, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed setting shipping info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting shipping info, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed setting shipping info, retrying..')
            time.sleep(delay)
            continue
        
        try:
            jsonATC = json.loads(r.text)
            if jsonATC['save']:
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully set shipping info!' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully set shipping info!')
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(jsonATC['errors'][0])+'] Failed setting shipping info, retrying..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[ERROR] ['+str(jsonATC['errors'][0])+'] [' + str(r.status_code) + '] Failed setting shipping info, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [' + str(r.status_code) + '] Failed setting shipping info, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] [' + str(r.status_code) + '] Failed setting shipping info, retrying..')
            time.sleep(delay)
            continue
        
    return proxy

def SetCourir(session, payment, prx):
    
    courir_payload = {
        'deliveryModeCode': 'ConsegnaBase'
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.unieuro.it',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Setting courir..' + utility.bcolors.ENDC)
    logging.info('[UNIEURO] ' + utility.threadTime(payment) + 'Setting courir..')

    while True:

        try:

            r = session.post('https://www.unieuro.it/online/cart/changeHomeDeliveryType', headers=headers, data=courir_payload, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting courir, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed setting courir, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting courir, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed setting courir, retrying..')
            time.sleep(delay)
            continue
        
        try:
            jsonATC = json.loads(r.text)
            if 'ok' in str(jsonATC['messages'][0]['code']):
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully set courir!' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully set courir!')
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting courir, retrying..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[ERROR] [' + str(r.status_code) + '] Failed setting courir, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [' + str(r.status_code) + '] Failed setting courir, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] [' + str(r.status_code) + '] Failed setting courir, retrying..')
            time.sleep(delay)
            continue
        
    return proxy

def FirstConfirm(session, payment, prx):
    
    payload = {
        'ship': 'on'
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.unieuro.it',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Getting checkout page..' + utility.bcolors.ENDC)
    logging.info('[UNIEURO] ' + utility.threadTime(payment) + 'Getting checkout page..')

    while True:

        try:

            r = session.post('https://www.unieuro.it/online/checkout/delivery', headers=headers, data=payload, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting checkout page, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed getting checkout page, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed getting checkout page, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed getting checkout page, retrying..')
            time.sleep(delay)
            continue
        
        if 'https://www.unieuro.it/online/checkout/payment' in r.url:
            print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Succesfully got checkout page!' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Succesfully got checkout page!')
            break
        else:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(r.url)+'] Failed getting checkout page, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[ERROR] ['+str(r.url)+'] [' + str(r.status_code) + '] Failed getting checkout page, retrying..')
            time.sleep(delay)
            continue
        
    return proxy

def SecondConfirm(session, payment, prx):
    
    payload = {
        'invoice': 'false',
        'modifiedBilling': '',
        'addressesToDelete': ''
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.unieuro.it',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Processing order..' + utility.bcolors.ENDC)
    logging.info('[UNIEURO] ' + utility.threadTime(payment) + 'Processing order..')

    while True:

        try:

            r = session.post('https://www.unieuro.it/online/checkout/address/modifyBillingAddress', headers=headers, data=payload, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] [1/2] Failed processing order, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] [1/2] Failed processing order, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [1/2] Failed processing order, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] [1/2] Failed processing order, retrying..')
            time.sleep(delay)
            continue
        
        try:
            jsonATC = json.loads(r.text)
            if jsonATC['save']:
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] [1/2] Successfully processed!' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [1/2] Successfully processed!')
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(jsonATC['errors'][0])+'] [1/2] Failed processing order, retrying..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[ERROR] ['+str(jsonATC['errors'][0])+'] [' + str(r.status_code) + '] [1/2] Failed processing order, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ' + str(r.status_code) + '] [1/2] Failed processing order, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] [' + str(r.status_code) + '] [1/2] Failed processing order, retrying..')
            time.sleep(delay)
            continue
        
    return proxy

def GetJSON(soup):

    orderData = soup.find('input', {'id':'orderData'})['value']
    #print(orderData)
    currencyCode = soup.find('input', {'id':'currencyCode'})['value']
    #print(currencyCode)
    shopperReference = soup.find('input', {'id':'shopperReference'})['value']
    #print(shopperReference)
    merchantReference = soup.find('input', {'id':'merchantReference'})['value']
    #print(merchantReference)
    skinCode = soup.find('input', {'id':'skinCode'})['value']
    #print(skinCode)
    shopperEmail = soup.find('input', {'id':'shopperEmail'})['value']
    #print(shopperEmail)
    merchantAccount = soup.find('input', {'id':'merchantAccount'})['value']
    #print(merchantAccount)
    shipBeforeDate = str(soup.find('input', {'id':'shipBeforeDate'})['value'])
    #print(shipBeforeDate)
    paymentAmount = soup.find('input', {'id':'paymentAmount'})['value']
    #print(paymentAmount)
    shopperLocale = soup.find('input', {'id':'shopperLocale'})['value']
    #print(shopperLocale)
    sessionValidity = str(soup.find('input', {'id':'sessionValidity'})['value'])
    #print(sessionValidity)
    allowedMethods = soup.find('input', {'id':'allowedMethods'})['value']
    #print(allowedMethods)
    merchantSig = soup.find('input', {'id':'merchantSig'})['value']
    #print(merchantSig)

    message_bytes = str(orderData).encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')

    pu = '{ "blockedMethods":"paypal", "orderData":"'+base64_message+'", "currencyCode":"'+currencyCode+'", "shopperReference":"'+ shopperReference+'", "merchantReference":"'+ merchantReference+'", "skinCode":"'+ skinCode+'", "shopperEmail":"'+ shopperEmail +'", "merchantAccount":"'+ merchantAccount+'", "shipBeforeDate":"'+ shipBeforeDate+'", "paymentAmount":"'+ paymentAmount+'", "shopperLocale":"'+ shopperLocale+'", "sessionValidity":"'+ sessionValidity+'", "allowedMethods":"'+ allowedMethods+'", "merchantSig":"'+ merchantSig+'" }'

    message_bytes = str(pu).encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode('ascii'), sessionValidity
 
def CheckoutCreditCard(session, payment, prx):
    
    payload = {
        'paymentMode': 'CartaCredito',
        'condition': 'true'
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.unieuro.it',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    proxy = prx

    while True:

        try:

            r = session.post('https://www.unieuro.it/online/checkout/payment', headers=headers, data=payload, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] [2/2] Failed processing order, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] [2/2] Failed processing order, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [2/2] Failed processing order, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] [2/2] Failed processing order, retrying..')
            time.sleep(delay)
            continue
        
        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            checkout, validTime = GetJSON(soup)

            print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[http://suerteofficial.altervista.org/unieuro_checkout.html?data=' + checkout + '] [' + str(r.status_code) + '] Successfully checked out!')
            setTitle(1)

            break
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [' + str(r.status_code) + '] [2/2] Failed processing order, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] [' + str(r.status_code) + '] [2/2] Failed processing order, retrying..')
            time.sleep(delay)
            continue
        
    return checkout, validTime

def CheckoutStore(session, payment, accountDict, prx):
    
    payload = {
        'contactPhone': accountDict['phone_number'],
        'onlinePayment': 'false'
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://www.unieuro.it',
        'referer': 'https://www.unieuro.it/online/checkout/delivery',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Processing order..' + utility.bcolors.ENDC)
    logging.info('[UNIEURO] ' + utility.threadTime(payment) + 'Processing order..')

    while True:

        try:

            r = session.post('https://www.unieuro.it/online/checkout/delivery', headers=headers, data=payload, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed processing order, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed processing order, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed processing order, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed processing order, retrying..')
            time.sleep(delay)
            continue
        
        if 'orderConfirmation' in r.url:
            checkout = str(r.url).split('/orderConfirmation/')[1]

            print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '['+checkout+'] [' + str(r.status_code) + '] Successfully checked out!')
            setTitle(1)
            break
        else:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [' + str(r.status_code) + '] Failed processing order, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[ERROR] [' + str(r.status_code) + '] Failed processing order, retrying..')
            time.sleep(delay)
            continue
        
    return checkout

def CheckoutPayPal(session, payment, prx):

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[UNIEURO] ' + utility.threadTime(payment) + 'Checking out..')

    while True:

        try:
            r = session.get('https://www.unieuro.it/online/checkout/paypalec/prepare', allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '429':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        if 'token' in r.url or 'payment.direct' in r.url:
            print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] ['+str(r.url)+'] Successfully checked out!')
            setTitle(1)
            break
        else:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[' + str(r.status_code) + '] [ERROR] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ERROR] Failed getting PayPal link, retrying..')
            time.sleep(delay)
            continue

    return r.url

def CheckoutPayPalFast(session, payment, sku, prx):

    atc_payload = {
        'serviceCode': '',
        'entryNumber': '0',
        'productCode': sku
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.unieuro.it',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }

    proxy = prx

    while True:

        try:

            r = session.post('https://www.unieuro.it/online/precart/paypalec/prepare', headers=headers, data=atc_payload, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed getting PayPal link, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed getting PayPal link, retrying..')
            time.sleep(delay)
            continue
        
        if 'token' in r.url or 'payment.direct' in r.url:
            print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] ['+str(r.url)+'] Successfully checked out!')
            setTitle(0)
            setTitle(1)
            break
        else:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] [' + str(r.status_code) + '] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[ERROR] [' + str(r.status_code) + '] Failed getting PayPal link, retrying..')
            time.sleep(delay)
            continue

    return r.url, proxy

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

def main(product, payment, mode, storeID, accountDict):

    validTime = ''
    prx = GetNewProxy()
    s = requests.session()

    if 'URL' in mode:
        sku, prx = ProductScraper(s, payment, product, prx)
    else:
        sku = product
    
    ##########################################

    start_time = datetime.now()

    if 'FAST' not in payment:
        print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Adding '+sku+' to cart..' + utility.bcolors.ENDC)
        logging.info('[UNIEURO] ' + utility.threadTime(payment) + 'Adding '+sku+' to cart..')

        url, title, img, prx = AddToCart(s, payment, sku, prx)

        if 'PP' in payment:
            checkout_link = CheckoutPayPal(s, payment, prx)
            payment = 'PayPal'
        elif 'CC' in payment:
            prx = SetAccount(s, payment, accountDict, prx)
            prx = SetAddress(s, payment, accountDict, prx)
            #prx = SetCourir(s, payment, prx)
            prx = FirstConfirm(s, payment, prx)
            prx = SecondConfirm(s, payment, prx)
            data, validTime = CheckoutCreditCard(s, payment, prx)
        else:
            prx = SetAccount(s, payment, accountDict, prx)
            prx = SetStore(s, payment, storeID, prx)
            checkout_link = CheckoutStore(s, payment, accountDict, prx)
            payment = 'Store'

    else:
        print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Getting PayPal link for '+sku + utility.bcolors.ENDC)
        logging.info('[UNIEURO] ' + utility.threadTime(payment) + 'Getting PayPal link for '+sku)

        url = 'https://www.unieuro.it/online/crissaio-pid'+sku
        title = sku
        img = 'https://media.discordapp.net/attachments/718845213652549673/778640995851304970/Unieuro-cuore-700x395.png'

        checkout_link, prx = CheckoutPayPalFast(s, payment, sku, prx)

        payment = 'PayPal Direct'

    final_time = datetime.now()-start_time
    
    ##########################################

    if 'CC' in payment:
        payment = 'Credit Card'
        tmp = 'http://suerteofficial.altervista.org/unieuro_checkout.html?data='+data
        checkout_link = utility.GetPasteBin(tmp)

        if 'pastebin' not in checkout_link:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + 'Failed getting checkout link with cookie, check debug file' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '['+str(tmp)+'] Failed getting checkout link with cookie, check debug file')
            time.sleep(100)

    elif 'PayPal' in payment:
        try:
            checkout_link = utility.getCheckoutLink(s, 'https://www.unieuro.it/online/', checkout_link)
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
            logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + ']Failed getting checkout link with cookie!')
            time.sleep(100)

    crissWebhook.sendUnieuroWebhook('Unieuro', url, accountDict['email'], title, 'None', checkout_link, img, payment, str(final_time), validTime, mode)
    crissWebhook.publicUnieuroWebhook('Unieuro', url, title, 'None', img, str(final_time), payment, mode)
    crissWebhook.staffUnieuroWebhook('Unieuro', url, 'None', img, str(final_time), mode)

    input('')
    time.sleep(100)

def start_main():

    title = utility.getTitleHeader() + "  -  Unieuro  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies 
        allProxies = utility.loadProxies('unieuro')
        with open('unieuro/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:
                try:
                    email = line['EMAIL']
                    name = line['FIRST NAME']

                    if('RANDOM' in email) and ('RANDOM' not in name):
                        name, email = utility.getCathcallEMail(line['LAST NAME'], email.replace('RANDOM', ''))
                        name = line['FIRST NAME']
                    elif('RANDOM' in email) and ('RANDOM' in name):
                        name, email = utility.getCathcallEMail(line['LAST NAME'], email.replace('RANDOM', ''))
                    elif('RANDOM' not in email) and ('RANDOM' in line['FIRST NAME']):
                        name = utility.getName()
                    
                    phone_number = line['PHONE']
                    if('RANDOM' in phone_number):
                        phone_number = utility.getRandomNumber()
                    
                    accountDict = {
                        'email':email,
                        'password':line['PASSWORD'],
                        'first_name':name,
                        'last_name':line['LAST NAME'],
                        'phone_number':phone_number,
                        'address':line['ADDRESS'],
                        'house_number':line['HOUSE NUMBER'],
                        'city':line['CITY'],
                        'zipcode':line['ZIPCODE'],
                        'province':line['PROVINCE']
                    }

                except Exception as e:
                    print(utility.threadTime(payment) + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                    logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] Failed loading task, please check csv file!')
                    input('Press ENTER to exit.')
                    sys.exit()
                
                if('PP' in line['PAYMENT']) or (line['PAYMENT'] == 'CC') or (line['PAYMENT'] == 'STORE'):

                    if 'https' in line['PRODUCT']:
                        mode = 'Direct URL'
                    else:
                        mode = 'PID'

                    t = Thread(target=main, args=(line['PRODUCT'], line['PAYMENT'], mode, line['STORE ID'], accountDict))
                    t.start()

                else:
                    print(utility.threadTime(payment) + utility.bcolors.FAIL + 'Failed loading task, please check payment method!' + utility.bcolors.ENDC)
                    logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + line['PAYMENT'] + '] Failed loading task, please check payment method!')
                    input('Press ENTER to exit.')
                    sys.exit()

    except Exception as e:
        print(utility.threadTime(payment) + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[UNIEURO] ' + utility.threadTime(payment) + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)

if __name__ == '__main__':
    start_main() 