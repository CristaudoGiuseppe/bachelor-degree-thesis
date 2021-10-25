# -*- coding: utf-8 -*-
#!/bin/env python

''' ALLIKE '''

import requests, signal, json, random, csv, time, sys, re, os, logging, utility, crissWebhook, cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, date
from threading import Thread, Lock
from os import system

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[ALLIKE] ' + utility.threadTime('') + str(exc_value))
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
    

    title = utility.getTitleHeader() + "  -  Allike  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()

def SizeScraper(session, url, mode, prx):

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
    logging.info('[ALLIKE] ' + utility.threadTime(mode) + 'Getting product info..')

    sizeDict = {}
    proxy = prx

    while True:

        try:
            r = session.post(url, proxies=proxy)

            if str(r.status_code) == '503':

                if 'Checking your browser before accessing' in str(r.text):
                    print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Found Cloudflare protection, retrying..' + utility.bcolors.ENDC)
                    logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Found Cloudflare protection, retrying..')
                    time.sleep(delay)
                    proxy = GetNewProxy()
                    continue
                else:
                    print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                    logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                    proxy = GetNewProxy()
                    time.sleep(delay)
                    continue
        
            soup = BeautifulSoup(r.text, 'html.parser')

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting size info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed getting size info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting size info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting size info, retrying..')
            time.sleep(delay)
            continue

        try:
            check = soup.find('div', {'id':'coming-soon-wrapper'}).text.replace('\n','')
            print(utility.threadTime(mode) + utility.bcolors.WARNING + '['+check+'] Product already not released, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '['+check+'] Product already not released, retrying..')
            time.sleep(delay)
            continue
        except:
            pass

        try:
            title = str(soup.find('title')).split('>')[1].split('<')[0]
            #print(title)
            
            img = soup.find('img', {'id':'image-0'})['src']
            #print(img)

            form_key = soup.find('input', {'name':'form_key'})['value']
            #print(form_key)

            product_id = soup.find('input', {'name':'product'})['value']
            #print(product_id)

            atc = soup.find('form', {'id': 'product_addtocart_form'})['action']
            #print(atc)

            super_attr = soup.find('select', {'class':'required-entry super-attribute-select no-display swatch-select'})['name']
            #print(super_attr)

        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [PULLED] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] [PULLED] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

        try:
            allSizes = soup.find_all('a', {'class':'swatch-link swatch-link-502'})

            for size in allSizes:
                sizeID = size['title']
                pid = str(size['id']).replace('swatch','')

                sizeDict.update({pid:sizeID})

            if len(sizeDict) == 0:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + 'Product out of stock, retrying..')
                time.sleep(delay)
                raise Exception
            else:
                break

        except Exception:
            try:
                sizeTemp = str(soup.select('#product-options-wrapper > script:nth-child(2)')[0]).split('(')[1].split(')')[0]
                sizeJSON = json.loads(sizeTemp)

                for size in sizeJSON['attributes'][super_attr.split('[')[1].split(']')[0]]['options']:
                    pid = size['id']
                    sizeID = str(size['label']).replace('\\/','/')
                    sizeDict.update({pid:sizeID})

                if len(sizeDict) == 0:
                    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                    logging.info('[ALLIKE] ' + utility.threadTime(mode) + 'Product out of stock, retrying..')
                    time.sleep(delay)
                    continue
                else:
                    break

            except Exception as e:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [SIZES] Failed getting size info, retrying..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] [SIZES] Failed getting size info, retrying..')
                time.sleep(delay)
                continue
            
    return title, img, form_key, product_id, atc, super_attr, sizeDict, proxy

def AddToCart(session, atc, product_id, form_key, super_attr ,size, sizeDict, url, size_main, mode, accountDict, prx):

    atc_payload = {
        'isAjax': 1,
        'form_key': form_key,
        'product': product_id,
        'related_product': '', 
        super_attr: size,
        #'product_id': '', 
        #'email_notification': '',
        #'parent_id': product_id,
        'return_url': ''
    }

    proxy = prx

    while True:
    
        try:
            r = session.post(atc+'?callback=', data=atc_payload, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

        try:
            itemBasket = json.loads('{"event":"viewBasket"'+str(r.text).split('{"event":"viewBasket"')[1].split(' );')[0])
            print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart! ['+itemBasket['item'][0]['id']+']' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [' + str(itemBasket) + '] Successfully added to cart! ['+itemBasket['item'][0]['id']+']')
            setTitle(0)
            break
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
            #Vecchio metodo usava solo questo -> main(url, size_main, mode, accountDict)
            #sys.exit()

    return proxy

def SetGuestCheckout(session, mode, prx):

    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Starting guest checkout..' + utility.bcolors.ENDC)
    logging.info('[ALLIKE] ' + utility.threadTime(mode) + 'Starting guest checkout..')

    while True:

        try:
            r = session.get('https://www.allikestore.com/default/checkout/onepage/', proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed starting guest checkout, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed starting guest checkout, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed starting guest checkout, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed starting guest checkout, retrying..')
            time.sleep(delay)
            continue
        
        try:
            checkSuccess = BeautifulSoup(r.text, 'html.parser').find('span', {'class':'number'}).text

            if '1' in checkSuccess:
                break
            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR 1] Failed starting guest checkout, retrying..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[ERROR 1] Failed starting guest checkout, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR 2] Failed starting guest checkout, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR 2] Failed starting guest checkout, retrying..')
            time.sleep(delay)
            continue

    return proxy

def SetBilling(session, form_key, accountDict, mode, prx):

    day, month, year = accountDict['birthday'].split('-')

    guest_payload = {
        'billing[address_id]': '', 
        'billing[firstname]': accountDict['first_name'],
        'billing[lastname]': accountDict['last_name'],
        'billing[company]': '',
        'billing[email]': accountDict['email'],
        'billing[street][]': accountDict['address'],
        'billing[city]': accountDict['city'],
        'billing[region_id]': '',
        'billing[region]': '',
        'billing[postcode]': accountDict['zipcode'],
        'billing[country_id]': accountDict['country_id'],
        'billing[telephone]': accountDict['phone_number'],
        'billing[fax]': '',
        'billing[month]': month,
        'billing[day]': day,
        'billing[year]': year,
        'billing[dob]': accountDict['birthday'],
        'billing[customer_password]': '', 
        'billing[confirm_password]': '', 
        'billing[save_in_address_book]': 1,
        'billing[use_for_shipping]': 1,
        'form_key': form_key
    }

    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Setting billing info..' + utility.bcolors.ENDC)
    logging.info('[ALLIKE] ' + utility.threadTime(mode) + 'Setting billing info..')

    while True:
        
        try:
            r = session.post('https://www.allikestore.com/default/checkout/onepage/saveBilling/', data=guest_payload, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed setting billing info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed setting billing info, retrying..')
            time.sleep(delay)
            continue
        
        try:
            solution = json.loads(r.text)

            if solution['goto_section'] == 'shipping_method' :
                print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '['+ str(r.status_code) + '] Successfully set billing info!' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '['+ str(r.status_code) + '] Successfully set billing info!')
                break
            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR 1] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(solution) + '] [ERROR 1] Failed setting billing info, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR 2] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR 2] Failed setting billing info, retrying..')
            time.sleep(delay)
            continue

    return proxy

def SetCourier(session, form_key, mode, country, prx):

    if 'DE' in country:
        shipping_method = 'premiumrate_DHL_GoGreen'
    else:
        shipping_method = 'premiumrate_UPS_Standard'

    guest_payload = {
        'shipping_method': shipping_method,
        'form_key': form_key
    }

    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Setting courier info..' + utility.bcolors.ENDC)
    logging.info('[ALLIKE] ' + utility.threadTime(mode) + 'Setting courier info..')


    while True:

        try:
            r = session.post('https://www.allikestore.com/default/checkout/onepage/saveShippingMethod/', data=guest_payload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting courier info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed setting courier info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed setting courier info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] setting courier info, retrying..')
            time.sleep(delay)
            continue

        try:
            solution = json.loads(r.text)

            if solution['goto_section'] == 'payment':
                print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully set courier info!' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Successfully set courier info!')
                break
            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR 1] Failed setting courier info, retrying..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(solution) + '] [ERROR 1] setting courier info, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR 2] Failed setting courier info, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR 2] setting courier info, retrying..')
            time.sleep(delay)
            continue

    return proxy

def CheckCreditCard(session, form_key, accountDict, mode, prx):

    params = {
        'aid': '41207', #account_id (di allike)
        'encoding': 'UTF-8',
        'errorurl': '',
        'hash': 'bebeda718a759da5a3e3daf7f7e9ff21',
        'integrator_name': '',
        'integrator_version': '',
        'key': '',
        'language': '',
        'mid': '37063', #mercant_id (di allike)
        'mode': 'live',
        'portalid': '2026657', #ok
        'request': 'creditcardcheck',
        'responsetype': 'JSON',
        'solution_name': '',
        'solution_version': '',
        'storecarddata': 'yes',
        'successurl': '',
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
    logging.info('[ALLIKE] ' + utility.threadTime(mode) + 'Checking out..')

    while True:

        try:
            r = session.get('https://secure.pay1.de/client-api/', params=params, proxies=proxy)
            
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            
            value = json.loads(str(r.text).replace('PayoneGlobals.callback(','').replace(');',''))

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking credit card, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed credit card, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed credit card, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed credit card, retrying..')
            time.sleep(delay)
            continue

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
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '['+value['errorcode']+'] ['+value['errormessage'] + '] Invalid credit card details, retrying..')
            time.sleep(delay)
            continue
    
    return ccDict, proxy

def CCheckout(session, form_key, ccDict, mode, prx):

    payloud= {
        'payment[method]': 'payone_creditcard',
        'payone_creditcard_cc_type_select': '4_'+ccDict['cardtp'],
        'payment[cc_type]': ccDict['cardtp'],
        'payment[payone_pseudocardpan]': ccDict['pseudo'],
        'payment[payone_cardexpiredate]': ccDict['cardexp'],
        'payment[cc_number_enc]': ccDict['truncate'],
        'payment[payone_config_payment_method_id]': '4',
        'payment[payone_config]': '{"gateway":{"4":{"aid":"41207","encoding":"UTF-8","errorurl":"","hash":"bebeda718a759da5a3e3daf7f7e9ff21","integrator_name":"","integrator_version":"","key":"","language":"","mid":"37063","mode":"live","portalid":"2026657","request":"creditcardcheck","responsetype":"JSON","solution_name":"","solution_version":"","storecarddata":"yes","successurl":""}}}',
        'payment[payone_config_cvc]': '{"4_V":"always","4_M":"always"}',
        'form_key': form_key,
        'agreement[2]': 1,
        'agreement[4]': 1,
        'customer_order_comment': ''
    }

    proxy = prx

    while True:

        try:
            r = session.post('https://www.allikestore.com/default/checkout/onepage/saveOrder/', data=payloud, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        try:
            result = json.loads(r.text)

            if result['success']:
                print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '['+ str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '['+ str(r.status_code) + '] ['+result['redirect']+']  Successfully checked out!')
                setTitle(1)
                break
            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [' + str(result['error_messages']) + '] Failed checking out, retrying..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(result['error_messages']) + '] [ERROR] Failed checking out, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

    return result['redirect']

def GetPayPal(session, mode, prx):

    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[ALLIKE] ' + utility.threadTime(mode) + 'Checking out..')

    while True:

        try:
            r = session.get('https://www.allikestore.com/default/paypal/express/start/button/1/', allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        if 'token' in r.url:
            print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Successfully checked out!')
            setTitle(1)
            break
        else:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.url) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

    return r.url

def PayPalFast(session, atc, product_id, form_key, super_attr ,size, sizeDict, url, size_main, mode, accountDict, prx):

    atc_payload = {
        'isAjax': 1,
        'form_key': form_key,
        'product': product_id,
        'related_product': '', 
        super_attr: size,
        'return_url': 'https://www.allikestore.com/default/paypal/express/start/button/1/'
    }

    proxy = prx

    while True:
    
        try:
            r = session.post(atc+'?callback=', data=atc_payload, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        
        if 'token' in r.url:
            print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Successfully checked out!')
            setTitle(1)
            break
        else:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[ALLIKE] ' + utility.threadTime(mode) + '[' + str(r.url) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue
            #Vecchio metodo usava solo questo -> main(url, size_main, mode, accountDict)
            #sys.exit()

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


def main(url, size, mode, accountDict):

    SetupCloudscraper()
    
    url = url.replace('/german/','/default/')
    
    prx = GetNewProxy()

    s = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'mobile': False,
            'platform': 'windows'
            #'platform': 'darwin'
        },captcha={'provider':'2captcha','api_key':api_key, 'no_proxy':True},
        doubleDown=False,
        requestPostHook=utility.injection,
        debug=False,
        cipherSuite='EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH'
    )

    while True:
        title, img, form_key, product_id, atc, super_attr, sizeList, prx = SizeScraper(s, url, mode, prx)
        pid, sizeID = utility.SelectSize(sizeList, size, mode, 'ALLIKE', configDict)
        
        if pid != -1 and sizeID != 1:
            break;

    start_time = datetime.now()

    if 'PP FAST' in mode:
        print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Getting PayPal link for size: ['+sizeID+']' + utility.bcolors.ENDC)
        logging.info('[ALLIKE] ' + utility.threadTime(mode) + 'Getting PayPal link for size: ['+sizeID+']')
        checkout = PayPalFast(s, atc, product_id, form_key, super_attr, pid, sizeList, url, size, mode, accountDict, prx)
    else:
        print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Adding to cart size: ['+sizeID+']' + utility.bcolors.ENDC)
        logging.info('[ALLIKE] ' + utility.threadTime(mode) + 'Adding to cart size: ['+sizeID+']')
        prx = AddToCart(s, atc, product_id, form_key, super_attr, pid, sizeList, url, size, mode, accountDict, prx)

        if 'PP' in mode:
            checkout = GetPayPal(s, mode, prx)
        elif 'CC' in mode:
            prx = SetGuestCheckout(s, mode, prx)
            prx = SetBilling(s, form_key, accountDict, mode, prx)
            prx = SetCourier(s, form_key, mode, accountDict['country_id'], prx)
            ccDict, prx = CheckCreditCard(s, form_key, accountDict, mode, prx)
            checkout = CCheckout(s, form_key, ccDict, mode, prx)

    final_time = utility.getFinalTime(start_time)

    try:
        checkout = utility.getCheckoutLink(s, 'https://www.allikestore.com/', checkout)
    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
        logging.info('[ALLIKE] ' + utility.threadTime('') + '[' + str(e) + ']Failed getting checkout link with cookie!')
        time.sleep(100)    

    crissWebhook.sendAllikeWebhook(url, title, sizeID, checkout, img, str(final_time), mode)
    crissWebhook.publicAllikeWebhook(url, title, sizeID, img, str(final_time), mode)
    crissWebhook.staffAllikeWebhook(url, title, sizeID, img, str(final_time), mode)
    
    input('')
    time.sleep(100)

def shockdrop(URL, val, mode):

    title = utility.getTitleHeader() + "  -  Allike  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    accountDict = {}

    try:
        global allProxies
        allProxies = utility.loadProxies('allike')
        with open('allike/task.csv', 'r') as csv_file:
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
                        logging.info('[ALLIKE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
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
                        logging.info('[ALLIKE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[ALLIKE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()

def start_main():

    title = utility.getTitleHeader() + "  -  Allike  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    
    try:
        global allProxies
        allProxies = utility.loadProxies('allike')
        with open('allike/task.csv', 'r') as csv_file:
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
                        logging.info('[ALLIKE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit()
                else:
                    try:
                        t = Thread(target=main, args=(line['URL'], line['SIZE'], line['PAYMENT'], ""))
                        t.start()
                    except Exception as e:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[ALLIKE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit()
    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[ALLIKE] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()

if __name__ == '__main__':
    start_main() 