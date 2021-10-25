# -*- coding: utf-8 -*-
#!/bin/env python

''' REVOLVE '''

import requests, signal, json, random, csv, time, sys, re, os, utility, crissWebhook
from bs4 import BeautifulSoup
from datetime import datetime, date
import logging
from threading import Thread, Lock
from os import system

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[REVOLVE] ' + utility.threadTime('') + str(exc_value))
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
    

    title = utility.getTitleHeader() + "  -  Revolve  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()

def ProductScraper(session, url, payment, prx):

    sizeDict = {}
    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
    logging.info('[REVOLVE] ' + utility.threadTime(payment) + 'Getting product info..')

    while True:

        try:
            r = session.get(url, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

        try:
            colorSelect = soup.find('button', {'class':'js-favorite-button favorite-button'})['data-code']
            csrfHash = r.text.split("var csrfHash = '")[1].split("';")[0]

            sizes = soup.findAll('input', {'class':'size-options__radio size-clickable'})
            
            for size in sizes:
                if size['data-qty'] != '0':
                    sizeDict.update({size['value']:size['data-size']})

            if len(sizeDict) == 0:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + 'Product out of stock, retrying..')
                time.sleep(delay)
                continue      
            else:    
                break

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(r.status_code)+'] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] ['+str(r.status_code)+'] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
    
    return colorSelect, csrfHash, sizeDict, proxy

def AddToCart(session, url, colorSelect, csrfHash, size, payment, prx):

    atc_payloud = {
        'colorSelect': colorSelect,
        'serialNumber': '',
        'sizeSelect': size,
        'sectionURL': 'Direct Hit',
        'sessionID': '$sessionID',
        'count': '',
        'csrfHash': csrfHash,
        'isMens': 'false',
        'd': 'Womens',
        'src': 'addtobag',
        'srcType': '',
        'qvclick': '-1',
        'contextReferrer': '',
        'addedFromFavorite': 'false',
        'fitItemSizes': '',
        'dateAdded': ''
    }

    proxy = prx

    while True:

        try:

            r = session.post('https://'+url+'/r/ajax/AddItemToBag.jsp', data=atc_payloud, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

        try:
            checkJSON = json.loads(r.text)
            if checkJSON['success']:
                productTitle = checkJSON['msg1']
                productIMG = checkJSON['msg2']
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully added to cart!')
                setTitle(0)
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(checkJSON['success'])+'] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[ERROR]['+str(checkJSON)+'] Failed adding to cart, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

    return productTitle, productIMG, proxy

def SetDeliveryOptions(session, url, accountDict, payment, prx):

    delivery_payloud = {
        'name': accountDict['name'],
        'street': accountDict['address'],
        'street2': '',
        'city': accountDict['city'],
        'state': accountDict['province'],
        'zip': accountDict['zipcode'],
        'country': accountDict['country_id'],
        'telephone': accountDict['phone_number'],
        'deliveryCode': '',
        'email': accountDict['email'],
        'pw': '',
        'verifypw': '',
        'create': 'false',
        'news': 'false',
        'autofilled': '{"name":false,"street":false,"street2":false,"city":false,"state":false,"zip":false,"telephone":false,"email":false}',
        'internationalID': '',
        'dateOfBirth': '',
        'karmir_luys': 'false',
        'g_recaptcha_response': ''
    }

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Setting delivery options..' + utility.bcolors.ENDC)
    logging.info('[REVOLVE] ' + utility.threadTime(payment) + 'Setting delivery options..')

    proxy = prx

    while True:

        try:
            r = session.post('https://'+url+'/r/ajax/SaveDeliveryOptions.jsp', data=delivery_payloud, allow_redirects=True, proxies=proxy)
            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting delivery options, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed setting delivery options, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting delivery options, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed setting delivery options, retrying..')
            time.sleep(delay)
            continue

        try:
            checkJSON = json.loads(r.text)
            if checkJSON['success']:
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully set delivery options!' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully set delivery options!')
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(checkJSON['success'])+'] Failed setting delivery options, retrying..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[ERROR]['+str(checkJSON)+'] Failed setting delivery options, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting delivery options, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed setting delivery options, retrying..')
            time.sleep(delay)
            continue

    return proxy

def PayPalFastPayment(session, url, payment, prx):

    header= {
        'Host': url,
        'Referer': 'https://'+url+'/r/ShoppingBag.jsp?navsrc=add_bag_with_ctl'
    }

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Getting PayPal link..' + utility.bcolors.ENDC)
    logging.info('[REVOLVE] ' + utility.threadTime(payment) + 'Getting PayPal link..')

    proxy = prx

    while True:

        try:
            r = session.post('https://'+url+'/r/expresscheckout.jsp?js=true&paymentType=PayPal&boid=-14101&pathreturn=%2Fr%2FReviewConfirm.jsp%3Fboid%3D-14100&pathcancel=%2Fr%2FShoppingBag.jsp', headers=header, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed getting PayPal link, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed getting PayPal link, retrying..')
            time.sleep(delay)
            continue

        try:
            checkJSON = json.loads(r.text)
            checkoutLink = 'https://www.paypal.com/webscr?cmd=_express-checkout&token=' + checkJSON['token']
            print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully checked out!')
            setTitle(1)
            break
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed sgetting PayPal link, retrying..')
            time.sleep(delay)
            continue

    return checkoutLink

def SetCoupon(session, url, coupon, payment, prx):

    payloud = {
        'promo': coupon,
        'scope': ''
    }

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Setting coupon..' + utility.bcolors.ENDC)
    logging.info('[REVOLVE] ' + utility.threadTime(payment) + 'Setting coupon..')

    proxy = prx

    while True:

        try:
            r = session.post('https://'+url+'/r/ajax/ApplyPromoCode.jsp', data=payloud, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting payment options, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed setting payment options, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting payment options, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed setting payment options, retrying..')
            time.sleep(delay)
            continue

        break

        '''
        try:
            checkJSON = json.loads(r.text)
            if checkJSON['success']:
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Coupon accepted!' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Coupon accepted!')
                setTitle(0)
                break
            else:
                if 'expired' in checkJSON['msg14']
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(checkJSON['success'])+'] Coupon expired, retrying..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[ERROR]['+str(checkJSON)+'] Failed setting payment options, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting payment options, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed setting payment options, retrying..')
            time.sleep(delay)
            continue
        '''

    return proxy

def SavePayment(session, url, accountDict, csrfHash, payment, prx):

    payment_payloud = {
        'credit': '',
        'id': '-1',
        'number': accountDict['credit_card'],
        'code': accountDict['cvv'],
        'expMonth': accountDict['month'],
        'expYear': accountDict['year'],
        'useShip': 'true',
        'name': '',
        'street': '',
        'street2': '',
        'city': '',
        'state': '',
        'zip': '',
        'country': accountDict['country_id'],
        'telephone': '',
        'internationalID': '',
        'installmentOption': '',
        'installmentOptionText': '',
        'installmentOptionRate': '',
        'csrfHash': csrfHash
    }

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Setting payment options..' + utility.bcolors.ENDC)
    logging.info('[REVOLVE] ' + utility.threadTime(payment) + 'Setting payment options..')

    proxy = prx

    while True:

        try:
            r = session.post('https://'+url+'/r/ajax/SavePaymentOptions.jsp', data=payment_payloud, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting payment options, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed setting payment options, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting payment options, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed setting payment options, retrying..')
            time.sleep(delay)
            continue

        try:
            checkJSON = json.loads(r.text)
            if checkJSON['success']:
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully set payment options!' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully set payment options!')
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(checkJSON['success'])+'] Failed setting payment options, retrying..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[ERROR]['+str(checkJSON)+'] Failed setting payment options, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting payment options, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed setting payment options, retrying..')
            time.sleep(delay)
            continue

    return proxy

def Checkout(session, url, payment, prx):

    alor = {
        'cccode_value': ''
    }

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[REVOLVE] ' + utility.threadTime(payment) + 'Checking out..')

    proxy = prx

    while True:

        try:
            r = session.post('https://'+url+'/r/ajax/SubmitOrder.jsp', data=alor, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        try:
            checkJSON = json.loads(r.text)
            if checkJSON['success']:
                orderNumber = checkJSON['msg0']
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] ['+str(checkJSON)+'] Successfully checked out!')
                setTitle(1)
                break
            else:
                orderNumber = 'fail'
                if str(checkJSON['msg0']) != '':
                    print(utility.threadTime(payment) + utility.bcolors.FAIL + '['+str(checkJSON['msg0'])+'] Payment declined..' + utility.bcolors.ENDC)
                else:
                    print(utility.threadTime(payment) + utility.bcolors.FAIL + 'Payment declined..' + utility.bcolors.ENDC)
                logging.info('[REVOLVE] ' + utility.threadTime(payment) + '['+str(checkJSON)+'] Payment declined..')
                time.sleep(delay)
                break
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue
            
    return orderNumber

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

def main(url, size, payment, coupon, accountDict):

    prx = GetNewProxy()
    s = requests.session()

    while True:
        colorSelect, csrfHash, sizeList, prx = ProductScraper(s, url, payment, prx)
        pid, sizeID = utility.SelectSize(sizeList, size, payment, 'Revolve', configDict)

        if pid != -1 and sizeID != 1:
            break
    
    productURL = url
    url = url.split('/')[2]

    start_time = datetime.now()
    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Adding to cart size: [' + sizeID + ']' + utility.bcolors.ENDC)
    logging.info('[REVOLVE] ' + utility.threadTime(payment) + 'Adding to cart size: [' + sizeID + ']')
    
    title, img, prx = AddToCart(s, url, colorSelect, csrfHash, pid, payment, prx)

    if coupon != '':
        prx = SetCoupon(s, url, coupon, payment, prx)

    if 'PP' in payment:
        link = PayPalFastPayment(s, url, payment, prx)
    else:
        prx = SetDeliveryOptions(s, url, accountDict, payment, prx)
        prx = SavePayment(s, url, accountDict, csrfHash, payment, prx)
        link = Checkout(s, url, payment, prx)
        
    final_time = utility.getFinalTime(start_time)

    if 'CC' not in payment:
        email = ''
        try:
            link = utility.getCheckoutLink(s, 'https://'+url+'/', link)
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
            logging.info('[REVOLVE] ' + utility.threadTime(payment) + '[' + str(e) + '] Failed getting checkout link with cookie!')
            time.sleep(100)
    else:
        email = accountDict['email']

    crissWebhook.sendRevolveWebhook(productURL, title, email, sizeID, link, img, final_time, payment)
    crissWebhook.publicRevolveWebhook(productURL, link, title, sizeID, img, final_time, payment)
    crissWebhook.staffRevolveWebhook(productURL, link, title, sizeID, img, str(final_time), payment)

    input('')
    time.sleep(100)

def shockdrop(URL, val, mode):

    title = utility.getTitleHeader() + "  -  Revolve  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies 
        allProxies = utility.loadProxies('revolve')

        with open('revolve/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:
               
                if 'CC' in mode:

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
                            'name':name+' '+line['LAST NAME'],
                            'phone_number':phone_number,
                            'address':line['ADDRESS'],
                            'zipcode':line['ZIPCODE'],
                            'city':line['CITY'],
                            'province':line['PROVINCE'],
                            'country_id':line['COUNTRY'],
                            'credit_card':line['CARD NUMBER'],
                            'month':line['EXP MONTH'],
                            'year':line['EXP YEAR'],
                            'cvv':line['CVV']
                        }

                        for tasks in range(0, val):
                            t = Thread(target=main, args=(URL, 'RANDOM', mode, line['COUPON'], accountDict))
                            t.start()

                        break

                    except Exception as e:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[REVOLVE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit(-1)

                else:
    
                    try:
                        for tasks in range(0, val):
                            t = Thread(target=main, args=(URL, 'RANDOM', mode, line['COUPON'], ''))
                            t.start()

                        break

                    except Exception as e:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[REVOLVE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit(-1)

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[REVOLVE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)

def start_main():

    title = utility.getTitleHeader() + "  -  Revolve  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies 
        allProxies = utility.loadProxies('revolve')

        with open('revolve/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:
               
                if 'CC' in line['PAYMENT']:
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
                            'name':name+' '+line['LAST NAME'],
                            'phone_number':phone_number,
                            'address':line['ADDRESS'],
                            'zipcode':line['ZIPCODE'],
                            'city':line['CITY'],
                            'province':line['PROVINCE'],
                            'country_id':line['COUNTRY'],
                            'credit_card':line['CARD NUMBER'],
                            'month':line['EXP MONTH'],
                            'year':line['EXP YEAR'],
                            'cvv':line['CVV']
                        }

                        t = Thread(target=main, args=(line['URL'], line['SIZE'], line['PAYMENT'], line['COUPON'], accountDict))
                        t.start()

                    except Exception as e:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[REVOLVE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit(-1)
                else:

                    try:

                        t = Thread(target=main, args=(line['URL'], line['SIZE'], line['PAYMENT'], line['COUPON'], ''))
                        t.start()

                    except Exception as e:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[REVOLVE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit(-1)

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[REVOLVE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)

if __name__ == '__main__':
    start_main() 