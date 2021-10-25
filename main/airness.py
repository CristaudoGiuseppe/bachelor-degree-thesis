# -*- coding: utf-8 -*-
#!/bin/env python

import requests, signal, json, random, csv, time, sys, re, os, utility, crissWebhook
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from os import system
from threading import Thread, Lock

''' AIRNESS '''

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[AIRNESS] ' + utility.threadTime('') + str(exc_value))
    input("Press ENTER to exit")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

os.chdir(os.path.dirname(sys.executable))
configDict = utility.getDictConfig()
delay = float(configDict.get('delay'))
all_proxies = None
proxy = None

headers_token = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'origin': 'https://airness.it',
    'authorization': 'Basic b01tNXJtOGdOZDJoS01UZHZfZGMxSFd4Q1BPZXBrZHRHd2FxLWFiczhudzo=',
    'content-type': 'application/x-www-form-urlencoded'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'authorization': '',
    'Cache-Control': 'no-cache, no-store',
    'content-type': 'application/vnd.api+json',
    'Pragma': 'no-cache',
    'origin': 'https://airness.it'
}

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
    

    title = utility.getTitleHeader() + "  -  Airness  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()

def CheckBanned(statusCode):
    
    if str(statusCode) == '503':
        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
        logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(statusCode) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
        time.sleep(delay)
        return True
    else:
        return False

def GettingToken(s, prx):

    payload_token = {
        'scope': 'market:2392',
        'grant_type': 'client_credentials'
    }

    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Getting token..' + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Getting token..')

    while True:

        try:
            r = s.post('https://airness-2.commercelayer.io/oauth/token', headers=headers_token, data=payload_token, proxies=proxy)

            if CheckBanned(r.status_code) is False:
                tokenJson = json.loads(r.text)
            else:
                proxy = GetNewProxy()

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting token, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting token, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting token, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting token, retrying..')
            time.sleep(delay)
            continue

        try:
            token = tokenJson['access_token']
            expires = tokenJson['expires_in']

            headers.update({'authorization':'Bearer '+token})

            print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully got token!'+ utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully got token!')
            print(utility.threadTime('') + utility.bcolors.WARNING + 'Token expires in: ' + str(expires) + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + 'Token expires in: ' + str(expires))
            break
        except:
            print(utility.threadTime('') + utility.bcolors.FAIL + '['+tokenJson['error']+'] Failed getting token, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] ['+tokenJson['error']+'] Failed getting token, retrying..')
            time.sleep(delay)
            continue

    return proxy

def GeneratingSession(s, prx):

    payload = '{"data": {"type": "orders","attributes": {"language_code": "it"}}}'

    proxy = prx

    print(utility.threadTime('') +  utility.bcolors.WARNING + 'Generating session..' + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Generating session..')

    while True:

        try:
            r = s.post('https://airness-2.commercelayer.io/api/orders', headers=headers, data=payload, proxies=proxy)
            
            if CheckBanned(r.status_code) is False:
                jsonSession = json.loads(r.text)
            else:
                proxy = GetNewProxy()

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed generating session, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed generating session, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed generating session, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed generating session, retrying..')
            time.sleep(delay)
            continue
        
        try:
            sessionID = jsonSession['data']['id']
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully got session!' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully got session! ['+str(sessionID)+']')
            break
        except:
            if(jsonSession['errors'][0]['detail'] == 'The access token you provided is invalid.'):
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+jsonSession['errors'][0]['detail']+'] Failed generating session, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+jsonSession['errors'][0]['detail']+'] Failed generating session, retrying..')
                time.sleep(delay)
                proxy = GettingToken(s, proxy)
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+jsonSession['errors'][0]['detail']+'] Failed generating session, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+jsonSession['errors'][0]['detail']+'] Failed generating session, retrying..')
                time.sleep(delay)
            
            continue

    return sessionID, proxy

def GettingProductInfo(s, productID, prx):

    params = {
        'content_type': 'node',
        'fields.slug[in]': productID,
        'fields.toRoot': 'true',
        'include': 10,
        'limit': 1,
        'locale': 'it-IT'
    }

    headersCdn = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'authorization': 'Bearer DV9XvUVfM7e4yj0PxpHnm-0Hz0SByyAXqOE6IS9iV4o'
    }

    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Getting product info: ' + productID + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Getting product info: ' + productID)

    while True:

        try:
            r = s.get('https://cdn.contentful.com/spaces/40i19ww9637w/environments/master/entries', headers=headersCdn, params=params, proxies=proxy)

            if CheckBanned(r.status_code) is False:
                productInfo = json.loads(r.text)
            else:
                proxy = GetNewProxy()

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

        try:
            title = str(productInfo['items'][0]['fields']['name']).replace("\\" ,"-")
            #print(title)
            img_url = 'http:'+str(productInfo['includes']['Asset'][0]['fields']['file']['url'])
            #print(img_url)
            sku = str(productInfo['items'][0]['fields']['seoTitle']).split('prodotto ')[1]
            #print(sku)
            break
        except Exception as e:
            try:
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+productInfo['message']+'] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] ['+productInfo['message']+'] Failed getting product info, retrying..')
                time.sleep(delay)
                continue
            except Exception as e:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[TOTAL:'+str(productInfo['total'])+'] Product page pulled, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [TOTAL:'+str(productInfo['total'])+'] Product page pulled, retrying..')
                time.sleep(delay)
                continue

    return title, img_url, sku, proxy

def GettinSizesInfo(s, sku, prx):

    params_sku = {
        'filter[q][reference_eq]': sku,
        'page[number]': 1,
        'page[size]': 25
    }

    sizeDict = {}
    proxy = prx

    while True:
        try:
            r = s.get('https://airness-2.commercelayer.io/api/skus', headers=headers, params=params_sku, proxies=proxy)
            
            if CheckBanned(r.status_code) is False:
                sizesJson = json.loads(r.text)
            else:
                proxy = GetNewProxy()
            
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting size info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting size info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting size info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting size info, retrying..')
            time.sleep(delay)
            continue

        try:
            if(sizesJson['errors'][0]['detail'] == 'The access token you provided is invalid.'):
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+sizesJson['errors'][0]['detail']+'] Failed getting size info, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+sizesJson['errors'][0]['detail']+'] Failed getting size info, retrying..')
                time.sleep(delay)
                proxy = GettingToken(s, proxy)
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+sizesJson['errors'][0]['detail']+'] Failed getting size info, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] ['+sizesJson['errors'][0]['detail']+'] Failed getting size info, retrying..')
                time.sleep(delay)
            continue
        except:
            for id in sizesJson['data']:
                sizeDict.update({id['id']:id['attributes']['metadata']['US']})

            if len(sizeDict) == 0:
                print(utility.threadTime('')+ utility.bcolors.WARNING + '['+str(r.status_code)+'] [ERROR] No sizes found, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+str(r.status_code)+'] [ERROR] No sizes found, retrying..')
                time.sleep(delay)
                continue
            else:
                break

    return sizeDict, proxy

def CheckInStockSizes(s, sizeDict, prx):

    inStockDict = {}
    proxy = prx
    
    print(utility.threadTime('') +  utility.bcolors.WARNING + 'Checking available sizes..' + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Checking available sizes..')
    
    while True:

        for key in sizeDict:

            try:
                r = s.get('https://airness-2.commercelayer.io/api/skus/'+key, headers=headers, proxies=proxy)
                
                if CheckBanned(r.status_code) is False:
                    checkStock = json.loads(r.text)
                else:
                    proxy = GetNewProxy()

            except requests.exceptions.ProxyError as errp:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            except requests.exceptions.ConnectionError as errh:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            except requests.exceptions.Timeout as errt:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed checking sizes, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed checking sizes, retrying..')
                time.sleep(delay)
                continue
            except Exception as e:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed checking sizes, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed checking sizes, retrying..')
                time.sleep(delay)
                continue
            
            try:
                if(checkStock['data']['attributes']['inventory']['available']):
                    inStockDict.update({key:sizeDict[key]})
            except Exception as e:
                if(checkStock['errors'][0]['detail'] == 'The access token you provided is invalid.'):
                    print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkStock['errors'][0]['detail']+'] Failed checking sizes, retrying..' + utility.bcolors.ENDC)
                    logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkStock['errors'][0]['detail']+'] Failed checking sizes, retrying..')
                    time.sleep(delay)
                    proxy = GettingToken(s, proxy)
                else:
                    print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkStock['errors'][0]['detail']+'] Failed checking sizes, retrying..' + utility.bcolors.ENDC)
                    logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] ['+checkStock['errors'][0]['detail']+'] Failed checking sizes, retrying..')
                    time.sleep(delay)

                continue

        if len(inStockDict) == 0:
            print(utility.threadTime('')+ utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + 'Product out of stock, retrying..')
            s.cookies.clear()
            time.sleep(delay)
            continue
        else:
            break


    return inStockDict, proxy

def AddToCart(s, pid, variant, carted, checkouted, prx):

    payload = '{"data": {"type": "line_items","attributes": {"quantity": "1","reference":"FkzzzMvVoxp21gZSBWjH"},"relationships": {"order": {"data": {"type": "orders","id": "'+pid+'"}},"item": {"data": {"type": "skus","id": "'+variant+'"}}}}}'
    
    proxy = prx

    while True:

        try:
            r = s.post('https://airness-2.commercelayer.io/api/line_items/', headers=headers, data=payload, proxies=proxy)

            if CheckBanned(r.status_code) is False:
                pass
            else:
                proxy = GetNewProxy()

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed adding to cart, retrgying..')
            time.sleep(delay)
            continue
        
        try:
            checkATC = json.loads(r.text)

            if(checkATC['errors'][0]['detail'] == 'The access token you provided is invalid.'):
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkATC['errors'][0]['detail']+'] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkATC['errors'][0]['detail']+'] Failed adding to cart, retrying..')
                time.sleep(delay)
                proxy = GettingToken(s, proxy)
            else:
                print(utility.threadTime('')+ utility.bcolors.FAIL + '['+checkATC['errors'][0]['detail']+'] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkATC['errors'][0]['detail']+'] Failed adding to cart, retrying..')
                time.sleep(delay)
            continue

        except:
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully added to cart!'+ utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '['+str(r.status_code)+'] Successfully added to cart!')
            setTitle(0)
            break

    return proxy

def AddCoupon(s, pid, couponCode, prx):

    payload = '{"data":{"type":"orders","id":"'+pid+'","attributes":{"coupon_code":"'+couponCode+'"}}}'

    params = {
        'include': 'line_items,billing_address,shipping_address,shipments.shipment_line_items.line_item,shipments.available_shipping_methods,shipments.shipping_method,available_payment_methods,payment_method,payment_source'
    }

    proxy = prx

    print(utility.threadTime('') +  utility.bcolors.WARNING + 'Adding coupon code..' + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Adding coupon code..')

    while True:

        try:
            r = s.patch('https://airness-2.commercelayer.io/api/orders/'+pid, headers=headers, params=params, data=payload, proxies=proxy)
        
            if CheckBanned(r.status_code) is False:
                pass
            else:
                proxy = GetNewProxy()
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed adding coupon code, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + utility.bcolors.FAIL + '[' + str(errt) + '] [TIMEOUT] Failed adding coupon code, retrying..' + utility.bcolors.ENDC)
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding coupon code, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + utility.bcolors.FAIL + '[' + str(e) + '] [ERROR] Failed adding coupon code, retrying..' + utility.bcolors.ENDC)
            time.sleep(delay)
            continue

        try:
            checkCoupon = json.loads(r.text)

            if(checkCoupon['errors'][0]['detail'] == 'The access token you provided is invalid.'):
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkCoupon['errors'][0]['detail']+'] Failed adding coupon code, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkCoupon['errors'][0]['detail']+'] Failed adding coupon code, retrying..')
                time.sleep(delay)
                proxy = GettingToken(s, proxy)
                continue
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkCoupon['errors'][0]['detail']+'] Failed adding coupon code, skipping this step..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] ['+checkCoupon['errors'][0]['detail']+'] Failed adding coupon code, skypping this step..')
                time.sleep(delay)
                break

        except:
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully set coupon code: ' + couponCode + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '['+str(r.status_code)+'] Successfully set coupon code: ' + couponCode)
            break

    return proxy

def SetCustomerEmail(s, pid, email, prx):

    params = {
        'include': 'line_items,billing_address,shipping_address,shipments.shipment_line_items.line_item,shipments.available_shipping_methods,shipments.shipping_method,available_payment_methods,payment_method,payment_source'
    }

    payload = '{"data":{"type":"orders","id":"'+pid+'","attributes":{"customer_email":"'+email+'"}}}'

    proxy = prx

    print(utility.threadTime('') +  utility.bcolors.WARNING + 'Selecting guest checkout..' + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Selecting guest checkout..')

    while True:

        try:
            r = s.patch('https://airness-2.commercelayer.io/api/orders/'+pid, headers=headers, params=params, data=payload, proxies=proxy)

            if CheckBanned(r.status_code) is False:
                pass
            else:
                proxy = GetNewProxy()
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed selecting guest checkout, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed selecting guest checkout, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed selecting guest checkout, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed selecting guest checkout, retrying..')
            time.sleep(delay)
            continue

        try:
            checkEmail = json.loads(r.text)

            if(checkEmail['errors'][0]['detail'] == 'The access token you provided is invalid.'):
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkEmail['errors'][0]['detail']+'] Failed selecting guest checkout, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkEmail['errors'][0]['detail']+'] Failed selecting guest checkout, retrying..')
                time.sleep(delay)
                proxy = GettingToken(s, proxy)
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkEmail['errors'][0]['detail']+'] Failed selecting guest checkout, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkEmail['errors'][0]['detail']+'] Failed selecting guest checkout, retrying..')  
                time.sleep(delay)
            
            continue
        except:
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully selected guest checkout!'+ utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '['+str(r.status_code)+'] Successfully selected guest checkout!')
            break

    return proxy

def SetCustomerAddress(s, accountDict, prx):

    payload = '{"data":{"type":"addresses","attributes":{"first_name":"'+accountDict['first_name']+'","last_name":"'+accountDict['last_name']+'","line_1":"'+accountDict['address']+'","line_2":"","city":"'+accountDict['city']+'","zip_code":"'+accountDict['zipcode']+'","state_code":"'+accountDict['province']+'","country_code":"'+accountDict['country']+'","phone":"'+accountDict['phone_number']+'","billing_info":""}}}'
    
    proxy = prx

    print(utility.threadTime('') +  utility.bcolors.WARNING + 'Setting personal address..' + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Setting personal address..')
    
    while True:

        try:
            r = s.post('https://airness-2.commercelayer.io/api/addresses', headers=headers, data=payload, proxies=proxy)

            if CheckBanned(r.status_code) is False:
                checkAddress = json.loads(r.text)
            else:
                proxy = GetNewProxy()

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed setting address, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed setting address, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed setting address, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed setting address, retrying..')
            time.sleep(delay)
            continue

        try:
            ship_id = checkAddress['data']['id']
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully set personal address!' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '['+str(r.status_code)+'] Successfully set personal address!')
            break
        except Exception as e:
            if(checkAddress['errors'][0]['detail'] == 'The access token you provided is invalid.'):
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkAddress['errors'][0]['detail']+'] Failed setting address, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkAddress['errors'][0]['detail']+'] Failed setting address, retrying..')
                time.sleep(delay)
                proxy = GettingToken(s, proxy)
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkAddress['errors'][0]['detail']+'] Failed setting address, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkAddress['errors'][0]['detail']+'] Failed setting address, retrying..')
                time.sleep(delay)   
            
            continue

    return ship_id, proxy

def SetBillingInfo(s, pid, ship_id, prx):

    params = {
        'include': 'line_items,billing_address,shipping_address,shipments.shipment_line_items.line_item,shipments.available_shipping_methods,shipments.shipping_method,available_payment_methods,payment_method,payment_source'
    }

    payload = '{"data":{"type":"orders","id":"'+pid+'","attributes":{"_shipping_address_same_as_billing":true},"relationships":{"billing_address":{"data":{"type":"addresses","id":"'+ship_id+'"}}}}}'

    payment_method_id = ''
    shipments_id = ''
    shipping_methods_id = ''
    proxy = prx

    print(utility.threadTime('') +  utility.bcolors.WARNING + 'Setting billing info..' + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Setting billing info..')
    
    while True:

        try:
            r = s.patch('https://airness-2.commercelayer.io/api/orders/'+pid, headers=headers, params=params, data=payload, proxies=proxy)

            if CheckBanned(r.status_code) is False:
                checkShip = json.loads(r.text)
            else:
                proxy = GetNewProxy()

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed setting billing info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed setting billing info, retrying..')
            time.sleep(delay)
            continue
        
        try:
            for id in checkShip['included']:

                if(id['type'] == 'payment_methods'):
                    payment_method_id = id['id']
                elif(id['type'] == 'shipments'):
                    shipments_id = id['id']
                elif(id['type'] == 'shipping_methods'):
                    shipping_methods_id = id['id']

            if payment_method_id != '' and shipments_id != '' and shipping_methods_id != '':
                print(utility.threadTime('') + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully set billing info!' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+str(r.status_code)+'] Successfully set billing info! ['+shipments_id+'] ['+shipping_methods_id+']')
                break
            else:
                ''' TEORICAMENTE SE SHIPMENTS_ID NON VIENE SETTATO E' OOS '''
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [OOS] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + utility.bcolors.FAIL + '[' + str(checkShip) + '] [ERROR] [OOS] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
                time.sleep(delay)
                continue

        except Exception as e:

            if(checkShip['errors'][0]['detail'] == 'The access token you provided is invalid.'):
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkShip['errors'][0]['detail']+'] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkShip['errors'][0]['detail']+'] Failed setting billing info, retrying..')
                time.sleep(delay)
                proxy = GettingToken(s, proxy)
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkShip['errors'][0]['detail']+'] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] ['+checkShip['errors'][0]['detail']+'] Failed setting billing info, retrying..')
                time.sleep(delay)    
            
            continue

    return payment_method_id, shipments_id, shipping_methods_id, proxy

def SetCourir(s, shipments_id, shipping_methods_id, prx):

    params = {
        'include':'shipment_line_items.line_item,available_shipping_methods,shipping_method'
    }

    payload = '{"data":{"type":"shipments","id":"'+shipments_id+'","relationships":{"shipping_method":{"data":{"type":"shipping_methods","id":"'+shipping_methods_id+'"}}}}}'

    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Setting shipping info..' + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Setting shipping info..')
    
    while True:

        try:    
            r = s.patch('https://airness-2.commercelayer.io/api/shipments/'+shipments_id, headers = headers, params=params, data=payload, proxies=proxy)

            if CheckBanned(r.status_code) is False:
                checkCourier = json.loads(r.text)
            else:
                proxy = GetNewProxy()

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed setting info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed setting shipping info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed setting shipping info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed setting shipping info, retrying..')
            time.sleep(delay)
            continue

        try:
            if(checkCourier['errors'][0]['detail'] == 'The access token you provided is invalid.'):
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkCourier['errors'][0]['detail']+'] Failed setting shipping info, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkCourier['errors'][0]['detail']+'] Failed setting shipping info, retrying..')
                time.sleep(delay)
                proxy = GettingToken(s, proxy)
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkCourier['errors'][0]['detail']+'] Failed setting shipping info, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] ['+checkCourier['errors'][0]['detail']+'] Failed setting shipping info, retrying..')
                time.sleep(delay)
            continue

        except:
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully set shipping info!'+ utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '['+str(r.status_code)+'] Successfully set shipping info!')
            break

    return proxy

def SetPayment(s, pid, payment_method_id, prx):

    params = {
        'include':'line_items,billing_address,shipping_address,shipments.shipment_line_items.line_item,shipments.available_shipping_methods,shipments.shipping_method,available_payment_methods,payment_method,payment_source'
    }

    payload = '{"data":{"type":"orders","id":"'+pid+'","relationships":{"payment_method":{"data":{"type":"payment_methods","id":"'+payment_method_id+'"}}}}}'

    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Setting payment info..' + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Setting payment info..')
    
    while True:

        try:
            r = s.patch('https://airness-2.commercelayer.io/api/orders/'+pid, headers = headers, params=params, data = payload, proxies=proxy)

            if CheckBanned(r.status_code) is False:
                pass
            else:
                proxy = GetNewProxy()
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed setting payment info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed setting payment info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed setting payment info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed setting payment info, retrying..')
            time.sleep(delay)
            continue

        try:
            checkPP = json.loads(r.text)

            if(checkPP['errors'][0]['detail'] == 'The access token you provided is invalid.'):
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkPP['errors'][0]['detail']+'] Failed setting payment info, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkPP['errors'][0]['detail']+'] Failed setting payment info, retrying..')
                time.sleep(delay)
                proxy = GettingToken(s, proxy)
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkPP['errors'][0]['detail']+'] Failed setting payment info, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkPP['errors'][0]['detail']+'] Failed setting payment info, retrying..')
                time.sleep(delay)

            continue
        except:
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully set payment!' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '['+str(r.status_code)+'] Successfully set payment!')
            break

    return proxy

def CompleteCheckout(s, pid, carted, checkouted, prx):

    firstURL = 'https://checkout.airness.it/'+pid+'/paypal'
    secondURL = 'https://checkout.airness.it/'+pid

    payload = '{"data":{"type":"paypal_payments","attributes":{"return_url":"'+firstURL+'","cancel_url":"'+secondURL+'"},"relationships":{"order":{"data":{"type":"orders","id":"'+pid+'"}}}}}'

    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Checking out..')
    
    while True:

        try:
            r = s.post('https://airness-2.commercelayer.io/api/paypal_payments', headers=headers, data=payload, proxies=proxy)
        
            if CheckBanned(r.status_code) is False:
                checkCheckout = json.loads(r.text)
            else:
                proxy = GetNewProxy()
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed checking out, retrgying..')
            time.sleep(delay)
            continue

        try:
            if(checkCheckout['errors'][0]['detail'] == 'The access token you provided is invalid.'):
                print(utility.threadTime('') + utility.bcolors.FAIL + '['+checkCheckout['errors'][0]['detail']+'] Failed checking out, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkCheckout['errors'][0]['detail']+'] Failed checking out, retrying..')
                time.sleep(delay)
                proxy = GettingToken(s, proxy)
            else:
                print(utility.threadTime('')+ utility.bcolors.FAIL + '['+checkCheckout['errors'][0]['detail']+'] Failed checking out, retrying..' + utility.bcolors.ENDC)
                logging.info('[AIRNESS] ' + utility.threadTime('') + '['+checkCheckout['errors'][0]['detail']+'] Failed checking out, retrying..')
                time.sleep(delay)
            continue

        except:
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + '['+str(r.status_code)+'] Successfully checked out!')
            checkouted = checkouted + 1
            setTitle(1)
            break

    return checkCheckout['data']['attributes']['approval_url']

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

def main(url, size, accountDict, couponCode, carted, checkouted):

    try:
        productID = url.split('/it/')[1]
    except:
        try:
            productID = url.split('/en/')[1]
        except:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed getting product info, check URL in CSV!' + utility.bcolors.ENDC)
            logging.info('[AIRNESS] ' + utility.threadTime('') + 'Failed getting product info, check URL in CSV!')
            input('Press ENTER to exit.')
            sys.exit(-1)

    prx = GetNewProxy()
    
    session = requests.session()
            
    prx = GettingToken(session, prx)

    pid, prx = GeneratingSession(session, prx)
    title, img_url, sku, prx = GettingProductInfo(session, productID, prx)
    sizeDict, prx = GettinSizesInfo(session, sku, prx)

    while True:
        inStockSizesDict, prx = CheckInStockSizes(session, sizeDict, prx)
        variant, sizeID = utility.SelectSize(inStockSizesDict, size, '', 'AIRNESS', configDict)

        if variant != -1 and sizeID != -1:     
            break

    start_time = datetime.now()
    print(utility.threadTime('') + utility.bcolors.WARNING + 'Adding to cart size ['+sizeID+']' + utility.bcolors.ENDC)
    logging.info('[AIRNESS] ' + utility.threadTime('') + 'Adding to cart size ['+sizeID+']')
    prx = AddToCart(session, pid, variant, carted, checkouted, prx)

    if(couponCode != ''):
        prx = AddCoupon(session, pid, couponCode, prx)
    
    prx = SetCustomerEmail(session, pid, accountDict['email'], prx)
    ship_id, prx = SetCustomerAddress(session, accountDict, prx)

    payment_method_id, shipments_id, shipping_methods_id, prx = SetBillingInfo(session, pid, ship_id, prx)
    prx = SetCourir(session, shipments_id, shipping_methods_id, prx)

    prx = SetPayment(session, pid, payment_method_id, prx)
    checkout_link = CompleteCheckout(session, pid, carted, checkouted, prx)

    final_time = datetime.now()-start_time

    crissWebhook.sendWebhook('Airness', url, accountDict['email'], title, sizeID, checkout_link, img_url, 'PayPal', final_time)
    crissWebhook.publicWebhook('Airness', url, title, sizeID, img_url, final_time, 'PayPal')
    crissWebhook.staffWebhook('Airness', title, sizeID, img_url, str(final_time))

    time.sleep(100)

def shockdrop(URL, val):

    title = utility.getTitleHeader() + "  -  Airness  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    accountDict = {}

    try:
        global allProxies 
        allProxies = utility.loadProxies('airness')
        with open('airness/task.csv', 'r') as csv_file:
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
                    elif('RANDOM' not in email) and ('RANDOM' in name):
                        name = utility.getName()
                    
                    phone_number = line['PHONE']
                    if('RANDOM' in phone_number):
                        phone_number = utility.getRandomNumber()

                    accountDict = {
                        'email':email,
                        'first_name':name,
                        'last_name':line['LAST NAME'],
                        'phone_number':phone_number,
                        'address':line['ADDRESS'],
                        'zipcode':line['ZIPCODE'],
                        'province':line['PROVINCE'],
                        'city':line['CITY'],
                        'country':line['COUNTRY']
                    }
                    
                    break

                except Exception as e:
                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading csv file!' + utility.bcolors.ENDC)
                    logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading csv file!')
                    input('Print ENTER to exit.')
                    sys.exit()
                
        for tasks in range(0, val):
            t = Thread(target=main, args=(URL, 'RANDOM', accountDict, "", carted, checkouted))
            t.start()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()

def start_main():

    title = utility.getTitleHeader() + "  -  Airness  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies 
        allProxies = utility.loadProxies('airness')
        with open('airness/task.csv', 'r') as csv_file:
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
                    elif('RANDOM' not in email) and ('RANDOM' in name):
                        name = utility.getName()
                    
                    phone_number = line['PHONE']
                    if('RANDOM' in phone_number):
                        phone_number = utility.getRandomNumber()

                    accountDict = {
                        'email':email,
                        'first_name':name,
                        'last_name':line['LAST NAME'],
                        'phone_number':phone_number,
                        'address':line['ADDRESS'],
                        'zipcode':line['ZIPCODE'],
                        'province':line['PROVINCE'],
                        'city':line['CITY'],
                        'country':line['COUNTRY']
                    }

                except Exception as e:
                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading csv file!' + utility.bcolors.ENDC)
                    logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading csv file!')
                    input('Print ENTER to exit.')
                    sys.exit()
                
                t = Thread(target=main, args=(line['URL'], line['SIZE'], accountDict, line['COUPON'], carted, checkouted))
                t.start()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[AIRNESS] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()

if __name__ == '__main__':
    start_main() 