# -*- coding: utf-8 -*-
#!/bin/env python

''' GROSBASKET '''

import requests, signal, json, random, csv, time, sys, re, os, cloudscraper, logging, utility, crissWebhook
from bs4 import BeautifulSoup
from datetime import datetime, date
from threading import Thread, Lock
from os import system

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[GROSBASKET] ' + utility.threadTime('') + str(exc_value))
    input("Press ENTER to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

os.chdir(os.path.dirname(sys.executable))
configDict = utility.getDictConfig()
delay = float(configDict.get('delay'))
api_key = configDict.get('2captcha')
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
    

    title = utility.getTitleHeader() + "  -  Grosbasket  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()

def ScrapeSize(s, product, prx):

    sizeDict = {}
    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
    logging.info('[GROSBASKET] ' + utility.threadTime('') + 'Getting product info..')

    while True:

        try:
            r = s.get(product, proxies=proxy)

            if str(r.status_code) == '503':

                if 'Checking your browser before accessing' in str(r.text):
                    print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Found Cloudflare protection, retrying..' + utility.bcolors.ENDC)
                    logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Found Cloudflare protection, retrying..')
                    proxy = GetNewProxy()
                    time.sleep(delay)
                    continue
                else:
                    print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                    logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                    proxy = GetNewProxy()
                    time.sleep(delay)
                    continue

            if str(r.status_code) == '429':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue

            soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

        try:
            productTitle = str(soup.find('li', {'class':'product'}).text).replace('\n','')
            productIMG = soup.find('a', {'id':'zoom-btn'})['href']
            category = str(soup.find('li', {'class':'nav-item level2 nav-1-3-10 classic'})).split('<a href="')[1].split('">')[0]
        except:
            try:
                productTitle = soup.find('meta', {'name':'keywords'})['content']
                productIMG = soup.find('img', {'alt':productTitle})['data-src']
                category = str(soup.find('li', {'class':'nav-item level2 classic'})).split('<a href="')[1].split('">')[0]
            except  Exception as e: 
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [PRODUCT INFO] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [PRODUCT INFO] Failed getting product info, retrying..')
                time.sleep(delay)
                continue
            
        try:
            form_key = soup.find('input', {'name':'form_key'})['value']
            product_id = soup.find('input', {'name':'product'})['value']
            super_attr = soup.find('select', {'class':'required-entry super-attribute-select'})['name']
        except  Exception as e: 
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [PULLED] Product pulled or not released yet, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [PULLED] Product pulled or not released yet, retrying..')
            time.sleep(delay)
            continue
        
        try:
            pidInStock = str(soup).split('var switcherConfig=')[1].split(',"images":')[0]+'}'
            pidInStockJson = json.loads(pidInStock)['stock']

            size = str(soup).split('Product.Config(')[1].split(');</script>')[0]
            sizeJson = json.loads(size)

            value = super_attr.split('[')[1].split(']')[0]

            for id in sizeJson['attributes'][value]['options']:
                pid = id['id']
                size = id['label']

                if pidInStockJson[id['products'][0]]:
                    sizeDict.update({pid:size})

            if len(sizeDict) == 0:
                print(utility.threadTime('') + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + 'Product out of stock, retrying..')
                time.sleep(delay)
                continue
            else:
                break

        except Exception as e: 
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [SIZES] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [SIZES] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

    return productTitle, productIMG, form_key, product_id, category, super_attr, sizeDict, proxy

def AddToCart(s, variant, product_id, form_key, super_attr, category, prx):

    payload = {
        'product_id': product_id,
        'form_key': form_key,
        'product': product_id,
        'related_product': '',
        super_attr: variant,
        'qty': '1',
        'IsProductView': '1',
        'current_category': category
    }

    proxy = prx

    while True:

        try:
            r = s.post('https://www.grosbasket.com/it/amcart/ajax/index/', data=payload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '429':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

        try:
            result = json.loads(r.text)

            if '1' in result['is_add_to_cart']:
                print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [' + str(result['count']) + '] Successfully added to cart!')
                setTitle(0)
                break
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR 1] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[ERROR 1] [' + str(result) + '] Failed adding to cart, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR 2] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR 2] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

    return proxy

def CheckoutToken(s, prx):

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Getting checkout token..' + utility.bcolors.ENDC)
    logging.info('[GROSBASKET] ' + utility.threadTime('') + 'Getting checkout token..')

    proxy = prx

    while True:

        try:
            r = s.get('https://www.grosbasket.com/it/firecheckout/', proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '429':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue

            soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting checkout token, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting checkout token, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting checkout token, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting checkout token, retrying..')
            time.sleep(delay)
            continue

        try:
            address_id = soup.find('input', {'name':'billing[address_id]'})['value']

            tmp = soup.find('input', {'class':'input-text qty'})
            cartid = tmp['name']
            cartAmount = tmp['value']
            cart_safe = cartid.replace('cart','cart_safe')

            deviceId = '{"device_session_id":"5877759187434dd4f6970958b23869a7"}'

            print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' +str(r.status_code) + '] Successfully got checkout token!'+ utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' +str(r.status_code) + '] Successfully got checkout token!')
            break
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting checkout token, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting checkout token, retrying..')
            time.sleep(delay)
            continue

    return address_id, cartid, cartAmount, cart_safe, deviceId, proxy

def Checkout(s, accountDict, address_id, cart_safe, cartAmount, cartid, deviceId, form_key, prx):

    checkout_payload = {
        'billing[address_id]': address_id,
        'billing[firstname]': accountDict['first_name'],
        'billing[lastname]': accountDict['last_name'],
        'billing[email]': accountDict['email'],
        'billing[telephone]': accountDict['phone_number'],
        'billing[street][]': accountDict['address'],
        'billing[postcode]': accountDict['zipcode'],
        'billing[city]': accountDict['city'],
        'billing[country_id]': accountDict['country'],
        'billing[region_id]': '',
        'billing[region]': '',
        'shipping[same_as_billing]': '1',
        'billing[company]': '', 
        'billing[vat_id]': '', 
        'billing[customer_password]': '',
        'billing[confirm_password]': '', 
        'billing[save_in_address_book]': '1',
        'billing[use_for_shipping]': '1',
        'shipping[address_id]': address_id,
        'shipping[firstname]': accountDict['first_name'],
        'shipping[lastname]': accountDict['last_name'],
        'shipping[telephone]': accountDict['phone_number'],
        'shipping[street][]': accountDict['address'],
        'shipping[postcode]': accountDict['zipcode'],
        'shipping[city]': '',
        'shipping[country_id]': accountDict['country'],
        'shipping[region_id]': '',
        'shipping[region]': '',
        'shipping[company]': '',
        'shipping[vat_id]': '',
        'shipping[save_in_address_book]': '1',
        'shipping_method': 'tablerate_bestway',
        'payment[method]': 'paypal_express',
        'coupon[remove]': '0',
        'coupon[code]': '', 
        'order-comment': ',',
        cart_safe: cartAmount,
        cartid: cartAmount,
        'payment[device_data]': deviceId,
        'review': '1',
    }

    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[GROSBASKET] ' + utility.threadTime('') + 'Checking out..')

    while True:

        try:
            r = s.post('https://www.grosbasket.com/it/firecheckout/index/saveOrder/form_key/'+form_key+'/', data=checkout_payload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '429':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        try:
            jsonCheck = json.loads(r.text)
            if 'paypal' in jsonCheck['redirect']:
                break
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [PAYPAL] Failed checking out, retrying..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[ERROR] [PAYPAL] Failed checking out, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [JSON] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [JSON] Failed checking out, retrying..')
            time.sleep(delay)
            continue

    return proxy

def GetPaypal(s, prx):

    proxy = prx

    while True:

        try:
            r = s.get('https://www.grosbasket.com/it/paypal/express/start/', allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '429':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        if 'token' in r.url:
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully checked out!')
            setTitle(1)
            break
        else:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[' + str(r.status_code) + '] [ERROR] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ERROR] Failed getting PayPal link, retrying..')
            time.sleep(delay)
            continue

    return r.url

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

def SetupCloudscraper():
    # ------------------------------------------------------------------------------ 
    #QUESTA PARTE NON DOVREBBE SERVIRE!
    # cloudscraper is not passing proxies to the requests module, thus we need to monkey
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    def perform_request(self, method, url, *args, **kwargs):
        if "proxies" in kwargs or "proxy"  in kwargs:
            return super(cloudscraper.CloudScraper, self).request(method, url, *args, **kwargs)
        else:
            return super(cloudscraper.CloudScraper, self).request(method, url, *args, **kwargs,proxies=self.proxies)
    # monkey patch the method in
    cloudscraper.CloudScraper.perform_request = perform_request
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------ 
    # SNS updated theire challenge strings leading to defualt cloudscraper regex not matching anymore thus monkey these as well
    # ------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------
    # cap challenge
    @staticmethod
    def is_New_Captcha_Challenge(resp):
        try:
            return (
                    cloudscraper.CloudScraper.is_Captcha_Challenge(resp)
                    and re.search(
                r'cpo.src\s*=\s*"/cdn-cgi/challenge-platform/?\w?/?\w?/orchestrate/captcha/v1"',
                resp.text,
                re.M | re.S
            )
                    and re.search(r'window._cf_chl_enter\(', resp.text, re.M | re.S)
            )
        except AttributeError:
            pass

        return False
    cloudscraper.CloudScraper.is_New_Captcha_Challenge = is_New_Captcha_Challenge

    # ------------------------------------------------------------------------------
    #normal challenge
    @staticmethod
    def is_New_IUAM_Challenge(resp):
        try:
            return (
                    resp.headers.get('Server', '').startswith('cloudflare')
                    and resp.status_code in [429, 503]
                    and re.search(
                r'cpo.src\s*=\s*"/cdn-cgi/challenge-platform/?\w?/?\w?/orchestrate/jsch/v1"',
                resp.text,
                re.M | re.S
            )
                    and re.search(r'window._cf_chl_enter\(', resp.text, re.M | re.S)
            )
        except AttributeError:
            pass

        return False
    cloudscraper.CloudScraper.is_New_IUAM_Challenge = is_New_IUAM_Challenge
    # ------------------------------------------------------------------------------


def main(url, size, accountDict):

    prx = GetNewProxy()

    s = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'mobile': False,
            'platform': 'windows'
            #'platform': 'darwin'
        },captcha={'provider':'2captcha','api_key':api_key, 'no_proxy':False},
        doubleDown=False,
        requestPostHook=utility.injection,
        debug=False,
        cipherSuite='EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH'
    )

    s.proxies = prx

    while True:
        title, img, fkey, pid, cat, sattr, sizeDict, prx = ScrapeSize(s, url, prx)
        variant, sizeID = utility.SelectSize(sizeDict, size, '', 'GROSBASKET', configDict)

        if variant != -1 and sizeID != -1:     
            break

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Adding to cart size: [' + sizeID + ']' + utility.bcolors.ENDC)
    logging.info('[GROSBASKET] ' + utility.threadTime('') + 'Adding to cart size: [' + sizeID + ']')

    start_time = datetime.now()
    prx = AddToCart(s, variant, pid, fkey, sattr, cat, prx)
    address_id, cartid, cartAmount, cart_safe, deviceId, prx = CheckoutToken(s, prx)
    prx = Checkout(s, accountDict, address_id, cartid, cartAmount, cart_safe, deviceId, fkey, prx)
    checkout_link = GetPaypal(s, prx)

    final_time = datetime.now()-start_time

    try:
        checkout_link = utility.getCheckoutLink(s, 'https://www.grosbasket.com/', checkout_link)
    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
        logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + ']Failed getting checkout link with cookie!')
        time.sleep(1000)

    crissWebhook.sendWebhook('Grosbasket', url, accountDict['email'], title, sizeID, checkout_link, img, 'PayPal', str(final_time))
    crissWebhook.publicWebhook('Grosbasket', url, title, sizeID, img, str(final_time), 'PayPal')
    crissWebhook.staffWebhook('Grosbasket', title, sizeID, img, str(final_time))
    
    input('')
    time.sleep(1000)

def shockdrop(URL, val):

    title = utility.getTitleHeader() + "  -  Grosbasket  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    accountDict = {}

    try:
        SetupCloudscraper()

        global allProxies
        allProxies = utility.loadProxies('grosbasket')
        
        with open('grosbasket/task.csv', 'r') as csv_file:
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
                        'city':line['CITY'],
                        'country':line['COUNTRY']
                    }

                    break

                except Exception as e:
                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                    logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                    input('Press ENTER to exit.')
                    sys.exit()

            for tasks in range(0, val):
                t = Thread(target=main, args=(URL, 'RANDOM', accountDict))
                t.start()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()

def start_main():

    title = utility.getTitleHeader() + "  -  Grosbasket  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies
        allProxies = utility.loadProxies('grosbasket')
        with open('grosbasket/task.csv', 'r') as csv_file:
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
                        'city':line['CITY'],
                        'country':line['COUNTRY']
                    }

                except Exception as e:
                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                    logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                    input('Press ENTER to exit.')
                    sys.exit()
                
                t = Thread(target=main, args=(line['URL'], line['SIZE'], accountDict))
                t.start()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[GROSBASKET] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()

if __name__ == '__main__':
    start_main() 