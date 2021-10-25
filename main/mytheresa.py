# -*- coding: utf-8 -*-
#!/bin/env python

''' MYTHERESA '''

import requests, signal, json, random, csv, time, sys, re, os, utility, crissWebhook
from bs4 import BeautifulSoup
from datetime import datetime, date
import logging
from threading import Thread, Lock
from os import system

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[MYTHERESA] ' + utility.threadTime('') + str(exc_value))
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
    

    title = utility.getTitleHeader() + "  -  Mytheresa  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'accept': 'application/vnd.lizards-and-pumpkins.product.v1+json',
    'Accept-Language': 'en-US,en;q=0.9',
    'pragma': 'no-cache',
    'Cache-Control': 'no-cache, no-store'
}

def ProductScraper(session, url, payment, prx):

    sizeDict = {}
    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
    logging.info('[MYTHERESA] ' + utility.threadTime(payment) + 'Getting product info..')

    while True:

        try:
            r = session.post(url, headers=header, proxies=proxy)
        
            if str(r.status_code) == '403':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

        try:
            productID = soup.find('input', {'name':'product'})['value']
            form_key = soup.find('input', {'name':'form_key'})['value']
            superAttr = soup.find('a', {'class':'addtocart-trigger'})['data-attributeid']

            for size in soup.findAll('a', {'class':'addtocart-trigger'}):
                sizeDict.update({size['data-option']:size.text.split(' ')[1]})

            if len(sizeDict) == 0:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + 'Product out of stock, retrying..')
                time.sleep(delay)
                continue      
            else:    
                break

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(r.status_code)+'] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] ['+str(r.status_code)+'] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
    
    return productID, form_key, superAttr, sizeDict, proxy

def AddToCart(session, form_key, productID, superAttr, size, country, payment, prx):

    atc_payloud = {
        'form_key': form_key,
        'product': productID,
        'related_product': '',
        'super_attribute['+superAttr+']': size
    }

    proxy = prx

    while True:

        try:

            r = session.post('https://www.mytheresa.com/en-'+country+'/ajaxcart/cart/add/', data=atc_payloud, headers=header, proxies=proxy)

            if str(r.status_code) == '403':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

        try:
            checkJSON = json.loads(r.text)
            if 'Item succcessfully added' in checkJSON['messages']:
                productInfo = json.loads(checkJSON['added_product_json'])
                productTitle = productInfo['name']
                productIMG = productInfo['image'].replace('//','')
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully added to cart!')
                setTitle(0)
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(checkJSON['messages'].split('<span>')[1].split('</span>')[0])+'] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[ERROR]['+str(checkJSON)+'] Failed adding to cart, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(r.status_code)+'] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] ['+str(r.status_code)+'] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

    return productTitle, productIMG, proxy

def SetGuestCheckout(session, country, payment, prx):

    proxy = prx
    sMethod = ''

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Starting guest checkout..' + utility.bcolors.ENDC)
    logging.info('[MYTHERESA] ' + utility.threadTime(payment) + 'Starting guest checkout..')

    while True:

        try:
            r = session.get("https://www.mytheresa.com/en-"+country+"/checkout/onepage/#login", proxies=proxy)

            if str(r.status_code) == '403':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
                
            soup = BeautifulSoup(r.text, 'html.parser')
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed starting guest checkout, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed starting guest checkout, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed starting guest checkout, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed starting guest checkout, retrying..')
            time.sleep(delay)
            continue
        
        try:
            addressID = soup.find('input', {'name':'shipping[address_id]'})['value']
            sMethod = soup.find('input', {'name':'shipping_method'})['value']

            for shippingMethod in soup.findAll('div', {'class':'shipping-method'}):
                soupShipping = BeautifulSoup(str(shippingMethod), 'html.parser')
                price = soupShipping.find('span', {'class':'price'}).text

                if '0,00' in price or '0.00' in price:
                    sMethod = soupShipping.find('input', {'name':'shipping_method'})['value']
                    break

            break
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(r.status_code)+'] Failed starting guest checkout, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed starting guest checkout, retrying..')
            time.sleep(delay)
            continue

    return addressID, sMethod, proxy

def SetBilling(session, addressID, accountDict, country, sMethod, payment, prx):

    guest_payload = {
        'shipping[address_id]': addressID, 
        'shipping[same_as_billing]': 1,
        'shipping[prefix]': 'Mr.',
        'shipping[suffix]': 'Dr.',
        'shipping[firstname]': accountDict['first_name'],
        'shipping[lastname]': accountDict['last_name'],
        'shipping[company]': '',
        'shipping[email]': accountDict['email'],
        'shipping[street][]': accountDict['address'] + accountDict['house number'],
        'shipping[house_number]': accountDict['house number'],
        'shipping[postcode]': accountDict['zipcode'],
        'shipping[city]': accountDict['city'],
        'shipping[country_id]': accountDict['country_id'],
        'shipping[telephone]': accountDict['phone_number'],
        'shipping[save_in_address_book]': 1,
        'shipping[use_for_shipping]': 1,
        'billing[address_id]': '', 
        'billing[suffix]': '',
        'billing[firstname]': '',
        'billing[lastname]': '',
        'billing[company]': '',
        'billing[street][]': '',
        'billing[street][]': '',
        'billing[postcode]': '',
        'billing[city]': '',
        'billing[country_id]': accountDict['country_id'],
        'billing[telephone]': '',
        'billing[save_in_address_book]': 1,
        'shipping_method': sMethod,
        'is_eco_package': '0',
        'giftoptions[277557754][type]': 'quote',
        'giftmessage[277557754][type]': 'quote',
        'giftmessage[277557754][to]': 'To',
        'giftmessage[277557754][from]': 'From'
    }

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Setting billing info..' + utility.bcolors.ENDC)
    logging.info('[MYTHERESA] ' + utility.threadTime(payment) + 'Setting billing info..')

    while True:
        
        try:
            r = session.post('https://www.mytheresa.com/en-'+country+'/checkout/onepage/saveDelivery/', data=guest_payload, proxies=proxy)

            if str(r.status_code) == '403':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed setting billing info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed setting billing info, retrying..')
            time.sleep(delay)
            continue
        
        try:
            solution = json.loads(r.text)

            if solution['goto_section'] == 'payment':
                print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '['+ str(r.status_code) + '] Successfully set billing info!' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '['+ str(r.status_code) + '] Successfully set billing info!')
                break
            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR 1] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(solution) + '] [ERROR 1] Failed setting billing info, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR 2] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR 2] Failed setting billing info, retrying..')
            time.sleep(delay)
            continue

    return proxy

def SetPayment(session, form_key, country, payment, prx):
    
    if 'BANK' in payment.upper():
        pym = 'checkmo'
    elif 'SOFORT' in payment.upper():
        pym = 'paymentnetwork_pnsofortueberweisung'

    order_payload = {
        'payment[method]': pym,
        'form_key': form_key,
        'agreement[1]': '1',
        'order_comment': ''
    }

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Submitting order..' + utility.bcolors.ENDC)
    logging.info('[MYTHERESA] ' + utility.threadTime(payment) + 'Submitting order..')

    while True:

        try:
            r = session.post('https://www.mytheresa.com/en-'+country+'/checkout/onepage/saveOrder/form_key/'+form_key, data=order_payload, proxies=proxy)

            if str(r.status_code) == '403':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed submitting order, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed submitting order, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed submitting order, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed submitting order, retrying..')
            time.sleep(delay)
            continue

        try:
            solution = json.loads(r.text)

            if solution['success']:

                if 'BANK' in payment.upper():
                    print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully submitted order!' + utility.bcolors.ENDC)
                    logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully submitted order!')
                    checkout = GetOrderNumber(session, country, payment, proxy)
                    break

                else:
                    checkout = solution['redirect'].replace('\/','')
                    print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
                    logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully checked out!')
                    setTitle(1)
                    break

            else:
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+solution['error_messages']+'] Failed submitting order, retrying..' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(solution) + '] [ERROR] Failed submitting order, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR 2] Failed submitting order, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR 2] Failed submitting order, retrying..')
            time.sleep(delay)
            continue

    return checkout

def GetOrderNumber(session, country, payment, prx):

    proxy = prx

    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Getting order number..' + utility.bcolors.ENDC)
    logging.info('[MYTHERESA] ' + utility.threadTime(payment) + 'Getting order number..')

    while True:
    
        try:
            r = session.get("https://www.mytheresa.com/en-"+country+"/checkout/onepage/success/", headers=header, proxies=proxy)
        
            if str(r.status_code) == '403':
                print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting order number, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(errt) + '] [TIMEOUT] Failed getting order number, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] Failed getting order number, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] Failed getting order number, retrying..')
            time.sleep(delay)
            continue

        try:
            orderID = str(r.text).split('Your order number is ')[1].split('</li>')[0]
            print(utility.threadTime(payment) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(r.status_code) + '] Successfully checked out!')
            setTitle(1)
            break

        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + '[ERROR] ['+str(r.status_code)+'] Failed getting order number, retrying..' + utility.bcolors.ENDC)
            logging.info('[MYTHERESA] ' + utility.threadTime(payment) + '[' + str(e) + '] [ERROR] ['+str(r.status_code)+'] Failed getting order number, retrying..')
            time.sleep(delay)
            continue

    return orderID
    
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

def main(url, size, payment, accountDict):

    country = accountDict['country_id'].lower()
    prx = GetNewProxy()
    s = requests.session()

    while True:
        productID, form_key, superAttr, sizeDict, prx = ProductScraper(s, url, payment, prx)
        pid, sizeID = utility.SelectSize(sizeDict, size, payment, 'Mytheresa', configDict)

        if pid != -1 and sizeID != 1:
            break

    start_time = datetime.now()
    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Adding to cart size: [' + sizeID + ']' + utility.bcolors.ENDC)
    logging.info('[MYTHERESA] ' + utility.threadTime(payment) + 'Adding to cart size: [' + sizeID + ']')
    
    title, img, prx = AddToCart(s, form_key, productID, superAttr, pid, country, payment, prx)

    addressID, sMethod, prx = SetGuestCheckout(s, country, payment, prx)
    prx = SetBilling(s, addressID, accountDict, country, sMethod, payment, prx)
    checkout = SetPayment(s, form_key, country, payment, prx)
    
    final_time = datetime.now()-start_time

    if 'SOFORT' in payment.upper():
        pym = 'Sofort'
        try:
            checkout = utility.getCheckoutLink(s, 'https://www.mytheresa.com/', checkout)
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime('') + '[' + str(e) + ']Failed getting checkout link with cookie!')
            time.sleep(100)
    else:
        pym = 'Bank Transfer'

    crissWebhook.sendWebhook('Mytheresa', url, accountDict['email'], title, sizeID, checkout, 'https://'+img, pym, str(final_time))
    crissWebhook.publicWebhook('Mytheresa', url, title, sizeID, 'https://'+img, str(final_time), pym)
    crissWebhook.staffWebhook('Mytheresa', title, sizeID, 'https://'+img, str(final_time))

    input('')
    time.sleep(100)

def shockdrop(URL, val):

    title = utility.getTitleHeader() + "  -  Mytheresa  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies 
        allProxies = utility.loadProxies('mytheresa')

        with open('mytheresa/task.csv', 'r') as csv_file:
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
                            'email':line['EMAIL'],
                            'first_name': name,
                            'last_name': line['LAST NAME'],
                            'phone_number':phone_number,
                            'address': line['ADDRESS'],
                            'house number': line['HOUSE NUMBER'],
                            'zipcode': line['ZIPCODE'],
                            'city': line['CITY'],
                            'country_id': line['COUNTRY']
                        }

                        for tasks in range(0, val):
                            t = Thread(target=main, args=(URL, 'RANDOM', 'BANK', accountDict))
                            t.start()

                        break

                    except Exception as e:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[MYTHERESA] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit(-1)

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[MYTHERESA] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)

def start_main():

    title = utility.getTitleHeader() + "  -  Mytheresa  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies 
        allProxies = utility.loadProxies('mytheresa')

        with open('mytheresa/task.csv', 'r') as csv_file:
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
                        'email':line['EMAIL'],
                        'first_name': name,
                        'last_name': line['LAST NAME'],
                        'phone_number':phone_number,
                        'address': line['ADDRESS'],
                        'house number': line['HOUSE NUMBER'],
                        'zipcode': line['ZIPCODE'],
                        'city': line['CITY'],
                        'country_id': line['COUNTRY']
                    }

                    t = Thread(target=main, args=(line['URL'], line['SIZE'], line['PAYMENT'], accountDict))
                    t.start()

                except Exception as e:
                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                    logging.info('[MYTHERESA] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                    input('Press ENTER to exit.')
                    sys.exit(-1)

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[MYTHERESA] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)

if __name__ == '__main__':
    start_main() 