# -*- coding: utf-8 -*-
#!/bin/env python

''' ASHPALT GOLD '''

import requests, signal, json, random, csv, time, sys, re, os, utility, crissWebhook
from bs4 import BeautifulSoup
from datetime import datetime, date
import logging
from threading import Thread, Lock

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[ASHPALT GOLD] ' + utility.threadTime('') + str(exc_value))
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
      

    title = utility.getTitleHeader() + "  -  AsphaltGold  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'accept': 'application/vnd.lizards-and-pumpkins.product.v1+json',
    'Accept-Language': 'en-US,en;q=0.9',
    'pragma': 'no-cache',
    'Cache-Control': 'no-cache, no-store',
    'Accept-Encoding': 'gzip, deflate',
    'referer': '',
    'origin': 'https://www.asphaltgold.com'
}

headersXML = {
    'Connection': 'keep-alive',
    'Origin': 'https://www.asphaltgold.com/en/',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}

def GetProductInfo(session, variant, mode, prx):

    sizeDict = {}
    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
    logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + 'Getting product info..')

    while True:

        try:
            r = session.get('https://d16xzy77usko0.cloudfront.net/api/product/?criteria=url_path%3A'+variant+'&snippetName=detail_de', headers=headers, proxies=proxy, timeout=15)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

        try:
            productJSON = json.loads(r.text)

            title = productJSON['data'][0]['attributes']['meta_title']

            if '0' in productJSON['data'][0]['attributes']['is_in_stock']:
                print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Product pulled or already not released..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + 'Product pulled or already not released..')
                time.sleep(delay)
                continue

            for line in productJSON['data'][0]['associated_products']:
                if('1' in str(line['attributes']['is_in_stock'])):
                    sizeDict.update({line['product_id']:line['attributes']['shoe_size']})

            if len(sizeDict) == 0:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + 'Product out of stock, retrying..')
                time.sleep(delay)
                continue
            else:    
                break

        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

    return title, sizeDict, proxy

def GetCardID(session, mode, prx):

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Getting cart..' + utility.bcolors.ENDC)
    logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + 'Getting cart..')

    proxy = prx

    while True:

        try:
            r = session.post('https://magento.asphaltgold-cloud.de/rest/de/V1/guest-carts', headers=headersXML, proxies=proxy, timeout=15)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting cart, retrying..')
            time.sleep(delay)
            continue

        try:
            if '"' in r.text:
                token = str(r.text).replace('"','')
                print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully got cart!' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] CartID: '+token)
                break
            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + ' [ERROR] Failed getting cart, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting cart, retrying..')
            time.sleep(delay)
            continue
    
    return token, proxy
     
def AddToCart(session, token, sku, mode, prx):

    headersATC = {
        'Host': 'api.asphaltgold.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'accept': 'application/json, text/plain, */*',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'Content-Type': 'application/json'
    }

    payloud = '{"cartItem": {"quote_id": "'+token+'", "sku": "'+sku+'", "qty": 1}}'

    proxy = prx

    while True:

        try:
            r = session.post('https://api.asphaltgold.com/V1/cart/rest/V1/guest-carts/'+token+'/items', headers=headersATC, data=payloud, proxies=proxy, timeout=8)
            
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

            jsonRespons = json.loads(r.text)

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

        try:
            item_id = jsonRespons['item_id']
            print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Successfully added to cart!')
            setTitle(0)
            break
        except Exception as e:
            try:
                if 'Die ausgewählte Größe ist nicht mehr verfügbar.' in jsonRespons['message']:
                    print(utility.threadTime(mode) + utility.bcolors.FAIL + '[OOS] Failed adding to cart, retrying ..' + utility.bcolors.ENDC)
                    logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [OOS] Failed adding to cart, retrying..')
            except:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
                
            time.sleep(delay)
            continue

    return proxy

def SetShippingInfo(session, token, accountDict, mode, prx):

    headersShip = {
        'Host': 'magento.asphaltgold-cloud.de',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'Content-Type': 'application/json'
    }

    payloud = '{"addressInformation": {"shippingAddress": {"firstname": "'+accountDict['first_name']+'", "lastname": "'+accountDict['last_name']+'", "company": "", "street": ["'+accountDict['address']+'", ""], "postcode": "'+accountDict['zipcode']+'", "city": "'+accountDict['city']+'", "country_id": "'+accountDict['country_id']+'", "telephone": "'+accountDict['phone_number']+'", "region_id": "81"}, "billingAddress": {"email": "'+accountDict['email']+'", "firstname": "'+accountDict['first_name']+'", "lastname": "'+accountDict['last_name']+'", "company": "", "street": ["'+accountDict['address']+'", ""], "postcode": "'+accountDict['zipcode']+'", "city": "'+accountDict['city']+'", "country_id": "'+accountDict['country_id']+'", "telephone": "'+accountDict['phone_number']+'", "region_id": "81"}, "shipping_carrier_code": "upsee", "shipping_method_code": "ups"}}'
    
    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Setting shipping info..' + utility.bcolors.ENDC)
    logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + 'Setting shipping info..')

    while True:

        try:
            r = session.post('https://magento.asphaltgold-cloud.de/rest/V1/guest-carts/'+token+'/shipping-information', headers=headersShip, data=payloud, proxies=proxy)
            
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting shipping info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed setting shipping info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(str(e))
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed setting shipping info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed setting shipping info, retrying..')
            time.sleep(delay)
            continue

        try:
            jsonRespons = json.loads(r.text)
            print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully set shipping info!' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Successfully set shipping info ['+str(jsonRespons['totals']['items'][0]['name'])+']')
            break
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed setting shipping info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed setting shipping info, retrying..')
            time.sleep(delay)
            continue

    return proxy

def CheckCreditCard(session, token, accountDict, mode, prx):

    headers = {
        'Host': 'secure.pay1.de',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'pragma': 'no-cache',
        'cache-control': 'no-cache'
    }

    params = {
        'aid': '42251', #account_id (di asphalt)
        'encoding': 'UTF-8',
        'mid': '41734', #mercant_id (di asphalt)
        'mode': 'live',
        'portalid': '2030243', #ok
        'request': 'creditcardcheck',
        'responsetype': 'JSON',
        'storecarddata': 'yes',
        'hash': '0b270276a79ee8690097d69b55fd7e285217f65dec70f73ad1821d22c8b45cb3107cff1d25a67fe62beca4a7bfdced88',
        'cardpan': accountDict['credit_card'],
        'cardexpiremonth': accountDict['month'],
        'cardexpireyear': accountDict['year'],
        'cardtype': '',
        'channelDetail': 'payoneHosted',
        'cardcvc2': accountDict['cvv'],
        'callback_method': 'PayoneGlobals.callback'
    }
    
    ccDict = {}
    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[ASPHALT GOLD] ' + utility.threadTime(mode) + 'Checking out..')

    while True:

        try:
            r = session.get('https://secure.pay1.de/client-api/', headers=headers, params=params, proxies=proxy)
            
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ASPHALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ASPHALT GOLD] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ASPHALT GOLD] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASPHALT GOLD] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASPHALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        try:
            value = json.loads(str(r.text).replace('PayoneGlobals.callback(','').replace(');',''))

            if 'VALID' in value['status']:

                ccDict = {
                    'pseudo': value['pseudocardpan'],
                    'truncate': value['truncatedcardpan'],
                    'cardexp': value['cardexpiredate'],
                    'cardtp': value['cardtype']
                }

                break
            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '['+value['errorcode']+'] ['+value['errormessage'] + '] Invalid credit card details, retrying..' + utility.bcolors.ENDC)
                logging.info('[ASPHALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] ['+value['errorcode']+'] ['+value['errormessage'] + '] [ERROR] Invalid credit card details, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [CC] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASPHALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] [CC] Failed checking out, retrying..')
            time.sleep(delay)
            continue
    
    return ccDict, proxy

def CompleteCheckout_1(session, token, accountDict, ccDict, mode, prx):

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Referer': 'https://www.asphaltgold.com/de/checkout/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Mobile Safari/537.36'
    }

    payloud= '{"email":"'+accountDict['email']+'","paymentMethod":{"method":"payone_creditcard","additional_data":{"status":"VALID","pseudocardpan":"'+ccDict['pseudo']+'","truncatedcardpan":"'+ccDict['truncate']+'","cardtype":"'+ccDict['cardtp']+'","cardexpiredate":"'+ccDict['cardexp']+'","errorcode":null,"errormessage":null,"payone_success_url":"https://www.asphaltgold.com/de/checkout/success","payone_cancel_url":"https://www.asphaltgold.com/de/payment/cancel","payone_error_url":"https://www.asphaltgold.com/de/payment/cancel"}},"billingAddress":{"email":"'+accountDict['email']+'","firstname":"'+accountDict['first_name']+'","lastname":"'+accountDict['last_name']+'","company":"","street":["'+accountDict['address']+'",""],"postcode":"'+accountDict['zipcode']+'","city":"'+accountDict['city']+'","country_id":"'+accountDict['country_id']+'","telephone":"'+accountDict['phone_number']+'","region_id":"0"}}'
    proxy = prx

    print(utility.threadTime(mode)+ utility.bcolors.WARNING+'[1/3] Completing checkout..'+ utility.bcolors.ENDC)

    while True:

        try:
            r = session.post('https://magento.asphaltgold-cloud.de/rest/de/V1/guest-carts/'+token+'/payment-information', headers=headers, data=payloud, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] [1/3] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] [1/3]  Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [1/3] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] [1/3] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        try:
            firstCode = str(r.text).replace('"','')
            if firstCode.isnumeric():
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Set first checkout step ['+firstCode+']')
                break
            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR 1] Failed setting first checkout step, retrying..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[ERROR 1] Failed setting first checkout step, retrying..')
                continue

        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR 2] Failed setting first checkout step, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR 2] Failed setting first checkout step, retrying..')
            time.sleep(delay)
            continue

    return firstCode, proxy

def CompleteCheckout_2(session, cc_code, mode, prx):

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.asphaltgold.com/de/checkout/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Mobile Safari/537.36'
    }

    proxy = prx

    print(utility.threadTime(mode)+ utility.bcolors.WARNING+'[2/3] Completing checkout..'+ utility.bcolors.ENDC)

    while True:

        try:
            r = session.get('https://magento.asphaltgold-cloud.de/rest/V1/orders/getincrement/'+cc_code, headers=headers, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] [2/3] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] [2/3] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [2/3] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] [2/3] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        
        try:
            secondCode = str(r.text).replace('"','')
            if secondCode.isnumeric():
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Set second checkout step ['+secondCode+']')
                break
            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR 1] [2/3] Failed checking out, retrying..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[ERROR 1] [2/3] Failed checking out, retrying..')
                continue

        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR 2] [2/3] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR 2] [2/3] Failed checking out, retrying..')
            time.sleep(delay)
            continue

    return secondCode, proxy

def CompleteCheckout_3(session, token, cc_code, mode, prx):
    
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.asphaltgold.com/de/checkout/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Mobile Safari/537.36'
    }

    proxy = prx

    print (utility.threadTime(mode)+ utility.bcolors.WARNING+'[3/3] Completing checkout..'+ utility.bcolors.ENDC)

    while True:

        try:
            r = session.get('https://magento.asphaltgold-cloud.de/rest/V1/payone/'+token+'/getredirect/'+cc_code, headers=headers, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] [3/3] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] [3/3] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [3/3] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] [3/3] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        try:
            finalJSON = json.loads(r.text)
            checkoutLink = str(finalJSON['redirect_url']).replace('\/', '/')

            print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Successfully checked out!' )
            setTitle(1)
            break

        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [3/3] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] [3/3] Failed checking out, retrying..')
            time.sleep(delay)
            continue

    return checkoutLink

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

def main(url, size, mode, accountDict):

    variant = str(url).split('/product/')[1].split('/')[0].replace('-','%2D')
    headers.update({'referer':url})

    prx = GetNewProxy()

    s = requests.session()

    while True:
        title, sizeDict, prx = GetProductInfo(s, variant, mode, prx)
        sku, sizeID = utility.SelectSize(sizeDict, size, mode, 'ASHPALTGOLD', configDict)
        
        if sku != -1 and sizeID != 1:
            break

    token, prx = GetCardID(s, mode, prx)

    start_time = datetime.now()
    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Adding to cart size: ['+sizeID+']' + utility.bcolors.ENDC)
    logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + 'Adding to cart size: ['+sizeID+']')
    prx = AddToCart(s, token, sku, mode, prx)

    if 'CC' in mode:
        prx = SetShippingInfo(s, token, accountDict, mode, prx)
        ccDict, prx = CheckCreditCard(s, token, accountDict, mode, prx)
        firstCode, prx = CompleteCheckout_1(s, token, accountDict, ccDict, mode, prx)
        secondCode, prx = CompleteCheckout_2(s, firstCode, mode, prx)
        checkoutLink = CompleteCheckout_3(s, token, secondCode, mode, prx)

        try:
            checkout = utility.getCheckoutLink(s, 'https://www.asphaltgold.com/de/', checkoutLink)
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
            logging.info('[ASHPALT GOLD] ' + utility.threadTime(mode) + '[' + str(e) + ']Failed getting checkout link with cookie!')
            time.sleep(1000)
    else:
        checkout = token

    final_time = datetime.now() - start_time

    crissWebhook.sendAGWebhook(url, title, sizeID, checkout, final_time, mode)
    crissWebhook.publicAGWebhook(url, title, sizeID, final_time, mode)
    crissWebhook.staffAGWebhook(url, title, sizeID, final_time, mode)
    
    input('')
    time.sleep(100)

def shockdrop(URL, val, mode):

    title = utility.getTitleHeader() + "  -  AsphaltGold  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    accountDict = {}

    try:
        global allProxies
        allProxies = utility.loadProxies('asphaltgold')
        with open('asphaltgold/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:

                if mode == 'CC':

                    try:
                        email = line['EMAIL']
                        name = line['FIRST NAME']

                        if('RANDOM' in email) and ('RANDOM' not in name):
                            name, email = utility.getCathcallEMail(line['LAST NAME'], email.replace('RANDOM', ''))
                            name = line['FIRST NAME']
                        elif('RANDOM' in email) and ('RANDOM' in name):
                            name, email = utility.getCathcallEMail(line['LAST NAME'], email.replace('RANDOM', ''))
                        elif('RANDOM' not in email) and ('RANDOM' in name):
                            name = utility.getName()
                        
                        phone_number = line['PHONE']
                        if('RANDOM' in phone_number):
                            phone_number = utility.getRandomNumber()
                        
                        birthday = utility.getBirthday()

                        accountDict = {
                            'email':email,
                            'first_name':name,
                            'last_name':line['LAST NAME'],
                            'phone_number':phone_number,
                            'birthday': birthday,
                            'address':line['ADDRESS'],
                            'zipcode':line['ZIPCODE'],
                            'city':line['CITY'],
                            'country_id':line['COUNTRY'],
                            'credit_card':line['CARD NUMBER'],
                            'month':line['EXP MONTH'],
                            'year':line['EXP YEAR'],
                            'cvv':line['CVV']
                        }

                        for tasks in range(0, val):
                            t = Thread(target=main, args=(URL, 'RANDOM', mode, accountDict))
                            t.start()

                        break

                    except Exception as e:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[ASPHALT GOLD] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit()
                else:

                    try:
                        for tasks in range(0, val):
                            t = Thread(target=main, args=(URL, 'RANDOM', mode, ""))
                            t.start()

                        break

                    except Exception as e:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[ASPHALT GOLD] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[ASPHALT GOLD] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()

def start_main():

    title = utility.getTitleHeader() + "  -  AsphaltGold  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies
        allProxies = utility.loadProxies('asphaltgold')
        with open('asphaltgold/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:

                if line['PAYMENT'] == 'CC':

                    try:
                        email = line['EMAIL']
                        name = line['FIRST NAME']

                        if('RANDOM' in email) and ('RANDOM' not in name):
                            name, email = utility.getCathcallEMail(line['LAST NAME'], email.replace('RANDOM', ''))
                            name = line['FIRST NAME']
                        elif('RANDOM' in email) and ('RANDOM' in name):
                            name, email = utility.getCathcallEMail(line['LAST NAME'], email.replace('RANDOM', ''))
                        elif('RANDOM' not in email) and ('RANDOM' in name):
                            name = utility.getName()
                        
                        phone_number = line['PHONE']
                        if('RANDOM' in phone_number):
                            phone_number = utility.getRandomNumber()
                        
                        
                        birthday = utility.getBirthday()

                        accountDict = {
                            'email':email,
                            'first_name':name,
                            'last_name':line['LAST NAME'],
                            'phone_number':phone_number,
                            'birthday': birthday,
                            'address':line['ADDRESS'],
                            'zipcode':line['ZIPCODE'],
                            'city':line['CITY'],
                            'country_id':line['COUNTRY'],
                            'credit_card':line['CARD NUMBER'],
                            'month':line['EXP MONTH'],
                            'year':line['EXP YEAR'],
                            'cvv':line['CVV']
                        }

                        t = Thread(target=main, args=(line['URL'], line['SIZE'], line['PAYMENT'], accountDict))
                        t.start()
                    except Exception as e:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[ASPHALT GOLD] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit()
                else:
                    try:
                        t = Thread(target=main, args=(line['URL'], line['SIZE'], line['PAYMENT'], ""))
                        t.start()
                    except Exception as e:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[ASPHALT GOLD] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[ASPHALT GOLD] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()

if __name__ == '__main__':
    start_main() 