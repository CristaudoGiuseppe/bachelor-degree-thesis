# -*- coding: utf-8 -*-
#!/bin/env python

''' CORNERSTREET '''

import requests, signal, json, random, csv, time, sys, re, os, utility, crissWebhook
import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import logging
from threading import Thread, Lock
from os import system

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[CORNERSTREET] ' + utility.threadTime('') + str(exc_value))
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
    

    title = utility.getTitleHeader() + "  -  Cornerstreet  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()


def Login(session, email, password, prx, pymM):

    login_payload = {
        'form_key': '',
        'login[username]': email,
        'login[password]': password,
        'send': ''
    }

    proxy = prx

    print(utility.threadTime(pymM) + utility.bcolors.WARNING + 'Logging in with: ' + email + utility.bcolors.ENDC)
    logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + 'Logging in with: ' + email)

    while True:

        try:

            r = session.get('https://www.cornerstreet.fr/customer/account/login/', proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[TIMEOUT] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errt) + '] [TIMEOUT] Failed loggin in, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] Failed loggin in, retrying..')
            time.sleep(delay)
            continue

        try:
            soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')
            form_key = soup.find('input', {'name':'form_key'})['value']
            login_payload.update({'form_key':form_key})

            break
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] [FORM_KEY] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] [FORM_KEY] Failed loggin in, retrying..')
            time.sleep(delay)
            continue


    while True:
    
        try:

            r = session.post('https://www.cornerstreet.fr/customer/account/loginPost/', data=login_payload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[TIMEOUT] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errt) + '] [TIMEOUT] Failed loggin in, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] Failed loggin in, retrying..')
            time.sleep(delay)
            continue

        if r.url == 'https://www.cornerstreet.fr/':
            print(utility.threadTime(pymM) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully logged in!' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) +  '[' + str(r.status_code) + '] Successfully logged in!')
            break
        else:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] [MAIL OR PASSWORD] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[ERROR] [MAIL OR PASSWORD] Failed loggin in, retrying..')
            time.sleep(delay)
            continue

    return proxy

def ScrapeProduct(session, url, prx, pymM):

    sizeDict = {}
    productIMG = ''
    proxy = prx

    print(utility.threadTime(pymM) + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
    logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + 'Getting product info..')

    while True:

        try:
            r = session.post(url, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue
            elif str(r.status_code) == '502':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Site down, retrying..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [CONNECTION ERROR] Site down, retrying..')
                proxy = GetNewProxy()
                continue

            soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[TIMEOUT] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errt) + '] [TIMEOUT] Failed loggin in, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] Failed loggin in, retrying..')
            time.sleep(delay)
            continue

        try:
            productIMG = soup.find('li', {'class':'col-md-6'})['data-src']
            #print(productIMG)
        except:
            pass


        try:
            productTitle = str(soup.find('li', {'class':'product'}).text).replace('\n','')
            #print(productTitle)

            atc_link = soup.find('form', {'id':'product_addtocart_form'})['action']
            #print(atc_link)

            super_attribute = soup.find('select', {'class':'required-entry super-attribute-select'})['name']
            #print(super_attribute)
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] [PULLED] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] [PULLED] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        
        try:
            sizeTemp = str(r.text.encode('utf-8')).split('var spConfig = new Product.Config(')[1].split(');')[0]
            sizeJSON = json.loads(sizeTemp)

            for size in sizeJSON['attributes'][super_attribute.split('[')[1].split(']')[0]]['options']:
                if '1' in size['is_in_stock']:
                    pid = size['id']
                    sizeID = str(size['label']).replace('\\/','/')
                    sizeDict.update({pid:sizeID})
            
            if len(sizeDict) == 0:
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + 'Product out of stock, retrying..')
                time.sleep(delay)
                continue
            else:
                break

        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] [SIZES] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] [SIZES] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

    return atc_link, super_attribute, sizeDict, productTitle, productIMG, proxy

def AddToCart(session, atc_link, super_attribute, id, prx, pymM):

    proxy = prx

    product = atc_link.split('/product/')[1].split('/')[0]
    #print(product)

    form_key = atc_link.split('/form_key/')[1].split('/')[0]
    #print(form_key)

    atc = atc_link+'?form_key='+form_key+'&product='+product+'&related_product=&'+super_attribute.replace('[','%5B').replace(']','%5D')+'='+id+'&qty=1'

    while True:
    
        try:

            r = session.post(atc, allow_redirects=True, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue

            soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[TIMEOUT] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errt) + '] [TIMEOUT] Failed loggin in, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] Failed loggin in, retrying..')
            time.sleep(delay)
            continue

        try:
            checkATC = soup.find('span', {'class':'count'}).text

            if '0' in checkATC:
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR 1] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[ERROR 1] Failed adding to cart, retrying..')
                time.sleep(delay)
                continue
            else:
                print(utility.threadTime(pymM) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] Successfully added to cart!')
                setTitle(0)
                break
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR 2] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR 2] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

    return form_key, proxy

def GetRegisterPage(session, url, prx, pymM):
    
    proxy = prx

    print(utility.threadTime(pymM) + utility.bcolors.WARNING + 'Starting guest checkout..' + utility.bcolors.ENDC)
    logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + 'Starting guest checkout..')

    while True:

        try:
            r = session.get('https://www.cornerstreet.fr/checkout/onepage/?register', proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            elif str(r.status_code) == '502':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Site down, retrying..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [CONNECTION ERROR] Site down, retrying..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

            soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[TIMEOUT] Failed starting guest checkout, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errt) + '] [TIMEOUT] Failed loggin in, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed starting guest checkout, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] Failed loggin in, retrying..')
            time.sleep(delay)
            continue

        try:
            checkSuccess = BeautifulSoup(r.text, 'html.parser').find('span', {'class':'number'}).text

            if '1' in checkSuccess:
                break
            else:
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR 1] Failed starting guest checkout, retrying..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[ERROR 1] Failed starting guest checkout, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR 2] Failed starting guest checkout, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR 2] Failed starting guest checkout, retrying..')
            time.sleep(delay)
            continue

    return proxy

def SetBilling(session, form_key, accountDict, prx, pymM):

    proxy = prx

    headerCF = dict(session.headers)
    headerCF.update({'content-type':'application/x-www-form-urlencoded'})
    day, month, year = utility.getBirthday().split('-')

    payload = 'billing%5Baddress_id%5D=&billing%5Bprefix%5D=Mr&billing%5Bfirstname%5D='+accountDict['first_name']+'&billing%5Blastname%5D='+accountDict['last_name']+'&billing%5Bcompany%5D=&billing%5Bemail%5D='+accountDict['email']+'&billing%5Bstreet%5D%5B%5D='+str(accountDict['address']).replace(' ','+')+'&billing%5Bcity%5D='+accountDict['city']+'&billing%5Bregion_id%5D=482&billing%5Bregion%5D=&billing%5Bpostcode%5D='+accountDict['zipcode']+'&billing%5Bcountry_id%5D='+accountDict['country_id']+'&billing%5Btelephone%5D='+accountDict['phone_number']+'&billing%5Bfax%5D=&billing%5Bday%5D='+day+'&billing%5Bmonth%5D='+month+'&billing%5Byear%5D='+year+'&billing%5Bdob%5D='+day+'%2F'+month+'%2F'+year+'&billing%5Bgender%5D=Sex&billing%5Bcustomer_password%5D='+accountDict['password']+'&billing%5Bconfirm_password%5D='+accountDict['password']+'&billing%5Bsave_in_address_book%5D=1&billing%5Buse_for_shipping%5D=1&form_key='+form_key
    
    print(utility.threadTime(pymM) + utility.bcolors.WARNING + 'Setting billing info..' + utility.bcolors.ENDC)
    logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + 'Setting billing info..')

    while True:
        
        try:
            r = session.post('https://www.cornerstreet.fr/checkout/onepage/saveBilling/', headers=headerCF, data=payload, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errt) + '] [TIMEOUT] Failed setting billing info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] Failed setting billing info, retrying..')
            time.sleep(delay)
            continue
        

        try:
            solution = json.loads(r.text)

            if solution['goto_section'] == 'shipping_method' :
                print(utility.threadTime(pymM) + utility.bcolors.OKGREEN + '['+ str(r.status_code) + '] Successfully set billing info!' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '['+ str(r.status_code) + '] Successfully set billing info!')
                break
            else:
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR 1] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(solution) + '] [ERROR 1] Failed setting billing info, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR 2] Failed setting billing info, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR 2] Failed setting billing info, retrying..')
            time.sleep(delay)
            continue

    return proxy

def SetCourier(session, form_key, telephone, prx, pymM):
    
    proxy = prx

    guest_payload = {
        'shipping_method': 'socolissimo_domicile_zone2',
        'tel_socolissimo': telephone,
        'form_key': form_key
    }

    print(utility.threadTime(pymM) + utility.bcolors.WARNING + 'Setting courier info..' + utility.bcolors.ENDC)
    logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + 'Setting courier info..')


    while True:

        try:
            r = session.post('https://www.cornerstreet.fr/checkout/onepage/saveShippingMethod/', data=guest_payload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting courier info, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errt) + '] [TIMEOUT] Failed setting courier info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed setting courier info, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] setting courier info, retrying..')
            time.sleep(delay)
            continue

        try:
            solution = json.loads(r.text)

            if solution['goto_section'] == 'payment' :
                print(utility.threadTime(pymM) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully set courier info!' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] Successfully set courier info!')
                break
            else:
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR 1] Failed setting courier info, retrying..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(solution) + '] [ERROR 1] setting courier info, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR 2] Failed setting courier info, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR 2] setting courier info, retrying..')
            time.sleep(delay)
            continue

    return proxy

def SetPaymentPayPal(session, form_key, prx, pymM):

    proxy = prx

    payload = {
        'payment[method]': 'paypal_express',
        'form_key': form_key,
        'amgdpr_agree': 1
    }

    print(utility.threadTime(pymM) + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + 'Checking out..')

    while True:

        try:
            r = session.post('https://www.cornerstreet.fr/checkout/onepage/saveOrder/form_key/'+form_key+'/', data=payload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] checking out, retrying..')
            time.sleep(delay)
            continue

        break

    while True:
    
        try:
            r = session.get('https://www.cornerstreet.fr/paypal/express/start/', allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..')
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..')
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..')
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        if 'token' in r.url:
            print(utility.threadTime(pymM) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] Successfully checked out!')
            setTitle(1)
            break
        else:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[' + str(r.status_code) + '] [ERROR] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ERROR] Failed getting PayPal link, retrying..')
            time.sleep(delay)
            continue
    
    return r.url

def SetPaymentAlma(session, form_key, prx, pymM):
    
    proxy = prx

    payload = {
        'payment[method]': 'alma_installments',
        'payment[installments_count]': '2',
        'form_key': form_key,
        'amgdpr_agree': 1
    }

    print(utility.threadTime(pymM) + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + 'Checking out..')

    while True:

        try:
            r = session.post('https://www.cornerstreet.fr/checkout/onepage/saveOrder/form_key/'+form_key+'/', data=payload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        try:
            result = json.loads(r.text)

            if result['success']:
                print(utility.threadTime(pymM) + utility.bcolors.OKGREEN + '['+ str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '['+ str(r.status_code) + '] ['+result['redirect']+']  Successfully checked out!')
                setTitle(1)
                break
            else:
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] [' + str(result['error_messages']) + '] Failed checking out, retrying..' + utility.bcolors.ENDC)
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(result['error_messages']) + '] [ERROR] Failed checking out, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

    return str(result['redirect']).replace('\/','/')

def Checkout(session, prx, pymM):

    proxy = prx

    print(utility.threadTime(pymM) + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + 'Checking out..')

    while True:

        try:
            r = session.get('https://www.cornerstreet.fr/paypal/express/start/', allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..')
                logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..')
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..')
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        if 'token' in r.url:
            print(utility.threadTime(pymM) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] Successfully checked out!')
            setTitle(1)
            break
        else:
            print(utility.threadTime(pymM) + utility.bcolors.FAIL + '[' + str(r.status_code) + '] [ERROR] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(r.status_code) + '] [ERROR] Failed getting PayPal link, retrying..')
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


def main(url, size, mode, accountDict):

    SetupCloudscraper()
    
    prx = GetNewProxy()

    if 'PAYPAL' in mode:
        pymD = 'PayPal'
        pymM = 'PP'
    else:
        pymD = 'Alma'
        pymM = 'ALM'

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

    if 'LOGIN' in mode:
        prx = Login(s, accountDict['email'], accountDict['password'], prx, pymM)
    else:
        pass

    while True:
        atc_link, super_attribute, sizeDict, productTitle, productIMG, prx = ScrapeProduct(s, url, prx, pymM)
        variant, sizeID = utility.SelectSize(sizeDict, size, pymM, 'CORNERSTREET', configDict)

        if variant != -1 and sizeID != 1:
            break;

    start_time = datetime.now()
    print(utility.threadTime(pymM) + utility.bcolors.WARNING + 'Adding to cart size ['+sizeID+']' + utility.bcolors.ENDC)
    logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + 'Adding to cart size ['+sizeID+']')
    form_key, prx = AddToCart(s, atc_link, super_attribute, variant, prx, pymM)
    
    if 'GUEST' in mode:
        prx = GetRegisterPage(s, url, prx, pymM)
        prx = SetBilling(s, form_key, accountDict, prx, pymM)
        prx = SetCourier(s, form_key, accountDict.get('phone_number'), prx, pymM)

        if 'PAYPAL' in mode:
            checkoutURL = SetPaymentPayPal(s, form_key, prx, pymM)
        else:
            checkoutURL = SetPaymentAlma(s, form_key, prx, pymM)
    else:
        checkoutURL = Checkout(s, prx, pymM)

    final_time = datetime.now()-start_time

    try:
        link = utility.getCheckoutLink(s, 'https://www.cornerstreet.fr/', checkoutURL)
    except Exception as e:
        print(utility.threadTime(pymM) + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
        logging.info('[CORNERSTREET] ' + utility.threadTime(pymM) + '[' + str(e) + '] Failed getting checkout link with cookie!')
        time.sleep(1000)    


    crissWebhook.sendWebhook('Cornerstreet', url, accountDict['email'], productTitle, sizeID, link, productIMG, pymD, final_time)
    crissWebhook.publicWebhook('Cornerstreet', url, productTitle, sizeID, productIMG, final_time, pymD)
    crissWebhook.staffWebhook('Cornerstreet', productTitle, sizeID, productIMG, str(final_time))

    input('')
    time.sleep(100)

def shockdrop(URL, val):

    title = utility.getTitleHeader() + "  -  Cornerstreet  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    accountDict = {}

    try:
        global allProxies
        allProxies = utility.loadProxies('cornerstreet')

        with open('cornerstreet/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:

                try:
                    email = line['EMAIL']
                    name = line['FIRST NAME']
                    
                    phone_number = line['PHONE']
                    if('RANDOM' in phone_number):
                        phone_number = utility.getRandomNumber()

                    for tasks in range(0, val):
                        name, email = utility.getCathcallEMail(line['LAST NAME'], line['EMAIL'].replace('RANDOM', ''))

                        accountDict = {
                            'email':email,
                            'password':line['PASSWORD'],
                            'first_name':name,
                            'last_name':line['LAST NAME'],
                            'phone_number':phone_number,
                            'address':line['ADDRESS'],
                            'zipcode':line['ZIPCODE'],
                            'city':line['CITY'],
                            'country_id':line['COUNTRY']
                        }

                        t = Thread(target=main, args=(URL, 'RANDOM', 'GUEST ALMA', accountDict))
                        t.start()

                    break

                except Exception as e:
                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                    logging.info('[CORNERSTREET] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                    input('Press ENTER to exit.')
                    sys.exit()
    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[CORNERSTREET] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()
            
def start_main():

    title = utility.getTitleHeader() + "  -  Cornerstreet  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies
        allProxies = utility.loadProxies('cornerstreet')

        with open('cornerstreet/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:

                if line['MODE'] == 'GUEST ALMA' or line['MODE'] == 'GUEST PAYPAL':

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
                            'password':line['PASSWORD'],
                            'first_name':name,
                            'last_name':line['LAST NAME'],
                            'phone_number':phone_number,
                            'address':line['ADDRESS'],
                            'zipcode':line['ZIPCODE'],
                            'city':line['CITY'],
                            'country_id':line['COUNTRY']
                        }

                        t = Thread(target=main, args=(line['URL'], line['SIZE'], line['MODE'], accountDict))
                        t.start()
                    except Exception as e:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[CORNERSTREET] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit()
                else:
                    if line['MODE'] == 'LOGIN PAYPAL':
                        try:

                            accountDict = {
                                'email': line['EMAIL'],
                                'password': line['PASSWORD']
                            }

                            t = Thread(target=main, args=(line['URL'], line['SIZE'], line['MODE'], accountDict))
                            t.start()
                        except Exception as e:
                            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                            logging.info('[CORNERSTREET] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                            input('Press ENTER to exit.')
                            sys.exit()
                    else:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                        logging.info('[CORNERSTREET] ' + utility.threadTime('') + 'Failed loading task, please check csv file!')
                        input('Press ENTER to exit.')
                        sys.exit()

                        
    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[CORNERSTREET] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()

if __name__ == '__main__':
    start_main()