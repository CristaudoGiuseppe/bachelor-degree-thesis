# -*- coding: utf-8 -*-
#!/bin/env python

''' AWLAB '''

import requests, signal, json, random, base64, codecs, csv, time, sys, re, os, utility, crissWebhook, js2py, cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, date
import logging
from threading import Thread, Lock
from os import system
from encrypter import ClientSideEncrypter
from cryptography.hazmat.primitives.ciphers.aead import AESCCM


def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[AWLAB] ' + utility.threadTime('') + str(exc_value))
    input("Press ENTER to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

os.chdir(os.path.dirname(sys.executable))
configDict = utility.getDictConfig()
delay = float(configDict.get('delay'))
api_key = configDict.get('2captcha')
allProxies = None
tokens = None

# --------------------------------------- #

PUB_EXPONENT = "10001"
MODULUS = "A58F2F0D8A4A08232DD1903F00A3F99E99BB89D5DEDF7A9612A3C0DC9FA9D8BDB2A20A233B663B0A48D47A0A1DDF1" \
        "64B3206985EFF19686E3EF75ADECF77BA10013B349C9F95CEBB5A66C48E3AD564410DB77A5E0798923E849E48A6274A" \
        "80CBE1ACAA886FF3F91C40C6F2038D90FABC9AEE395D4872E24183E8B2ACB28025964C5EAE8058CB06288CDA80D44F6" \
        "9A7DFD3392F5899886094DB23F703DAD458586338BF21CF84288C22020CD2AB539A35BF1D98582BE5F79184C84BE877" \
        "DB30C3C2DE81E394012511BFE9749E35C3E40D28EE3338DE7CBB1EDD253951A7B66A85E9CC920CA2A40CAD48ACD8BD1" \
        "AE681997D1655E59005F1887B872A7A873EDBD1"

# --------------------------------------- #
'''
harvester = Harvester()
tokens = harvester.intercept_recaptcha_v2(
    domain='aw-lab.com',
    sitekey='6LdRe9AZAAAAAOS-JQBuz5dGCulWkezaVBx8hwm7')
'''
# --------------------------------------- #

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
    

    title = utility.getTitleHeader() + "  -  AWLAB  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()

def GetProductSource(pid, country):

    if 'www' in pid or 'es' in pid or 'en' in pid:
        source = pid
    else:
        if 'IT' in country:
            source = 'https://www.aw-lab.com/on/demandware.store/Sites-awlab-'+country.lower()+'-Site/'+country.lower()+'_'+country+'/Product-Variation?pid='+pid+'&format=ajax'
        elif 'ES' in country:
            source = 'https://'+country.lower()+'.aw-lab.com/on/demandware.store/Sites-awlab-'+country.lower()+'-Site/'+country.lower()+'_'+country+'/Product-Variation?pid='+pid+'&format=ajax'
        else:
            source = 'https://www.en.aw-lab.com/on/demandware.store/Sites-awlab-en-Site/en_'+country+'/Product-Variation?pid='+pid+'&format=ajax'

    return source

def CheckProductInfo(session, pid, mode, country, prx):

    sizeDict = {}
    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
    logging.info('[AWLAB] ' + utility.threadTime(mode) + 'Getting product info..')

    source = GetProductSource(pid, country)

    while True:
    
        try:
            r = session.get(source, proxies=proxy)
            
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '429':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

        try:
            soup = BeautifulSoup(r.text, "html.parser")

            allSizes = soup.find_all('a', {'class':'b-size-selector__link'})

            for size in allSizes:
                variant = size['data-variant-id']
                #print(variant)
                sizeID = size['title']
                #print(sizeID)

                if(variant in sizeDict):
                    pass
                else:
                    sizeDict.update({variant:sizeID})
            
            if len(sizeDict) == 0:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + 'Product out of stock, retrying..')
                time.sleep(delay)
                continue
            else:
                break

        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Product page pulled or already not released, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Product page pulled or already not released, retrying..')
            time.sleep(delay)
            continue

    return sizeDict, proxy

def AddToCart(session, variant, mode, country, prx):

    atc_data = {
        'Quantity': 1,
        'sizeTable': '',
        'cartAction': 'add',
        'pid': variant
    }

    if 'IT' in country:
        atc_link = 'https://www.aw-lab.com/on/demandware.store/Sites-awlab-'+country.lower()+'-Site/'+country.lower()+'_'+country+'/Cart-AddProduct?format=ajax'
    elif 'ES' in country:
        atc_link = 'https://'+country.lower()+'.aw-lab.com/on/demandware.store/Sites-awlab-'+country.lower()+'-Site/'+country.lower()+'_'+country+'/Cart-AddProduct?format=ajax'
    else:
        atc_link = 'https://en.aw-lab.com/on/demandware.store/Sites-awlab-en-Site/en_'+country+'/Cart-AddProduct?format=ajax'

    proxy = prx

    while True:

        try:
            r = session.post(atc_link, data=atc_data, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '429':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue
                
            soup = BeautifulSoup(r.text, 'html.parser')

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

        try:
            if '1' in str(soup.find('span', {'class':'b-utility-menu__quantity'}).text).replace('\n',''):

                info = soup.find('a', {'class':'b-minicart__centred-container'})

                productURL = str(info['href'])
                #print(productURL)
                productName = str(info['title']).replace('Vai al prodotto: ','').replace('Ir al producto ','').replace('Go to the product ','')
                #print(productName)
                productIMG = str(info).split('data-lazy="')[1].split('?')[0]
                #print(productIMG)

                print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Successfully added to cart!')
                setTitle(0)
                break
            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [OOS] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[ERROR] [OOS] Failed adding to cart, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

    return productURL, productName, productIMG, proxy
     
def GetCheckoutToken(session, mode, country, prx):

    if 'IT' in country:
        shipping_link = 'https://www.aw-lab.com/shipping'
    elif 'ES' in country:
        shipping_link = 'https://'+country.lower()+'.aw-lab.com/shipping'
    else:
        shipping_link = 'https://en.aw-lab.com/shipping'

    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Getting checkout token..' + utility.bcolors.ENDC)
    logging.info('[AWLAB] ' + utility.threadTime(mode) + 'Getting checkout token..')

    while True:

        try:
            r = session.get(shipping_link, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '429':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting checkout token, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed getting checkout token, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting checkout token, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting checkout token, retrying..')
            time.sleep(delay)
            continue
        
        try:
            token = BeautifulSoup(r.text, 'html.parser').find('input', {'name':'csrf_token'})['value']
            phone_code = BeautifulSoup(r.text, 'html.parser').find('option', {'selected':"selected"})['value']

            print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully got checkout token!' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Successfully got checkout token!')
            break
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [OOS] Failed getting checkout token, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] [OOS] Failed getting checkout token, retrying..')
            time.sleep(delay)
            continue

    return token, phone_code, proxy

def StartCheckout(session, token, accountDict, mode, phone_code, country, prx):

    if 'IT' in country:
        save = 'Procedi al pagamento'
        shipping_link = 'https://www.aw-lab.com/on/demandware.store/Sites-awlab-'+country.lower()+'-Site/'+country.lower()+'_'+country+'/COShipping-SingleShipping'
    elif 'ES' in country:
        save = 'Ir a la caja'
        shipping_link = 'https://'+country.lower()+'.aw-lab.com/on/demandware.store/Sites-awlab-'+country.lower()+'-Site/'+country.lower()+'_'+country+'/COShipping-SingleShipping'
    else:
        save = 'Proceed to Checkout'
        shipping_link = 'https://en.aw-lab.com/on/demandware.store/Sites-awlab-en-Site/en_'+country+'/COShipping-SingleShipping'
    
    birthday = utility.getAWLABBirthday()
    day, month, year = birthday.split('-')

    proxy = prx

    fatturazione_payload = {
        'dwfrm_billing_billingAddress_email_emailAddress': accountDict['email'],
        'dwfrm_singleshipping_shippingAddress_addressFields_phonecountrycode_codes': phone_code,
        'dwfrm_singleshipping_shippingAddress_addressFields_phonewithoutcode': accountDict['phone_number'],
        'dwfrm_singleshipping_shippingAddress_addressFields_phone': phone_code+accountDict['phone_number'],
        'dwfrm_singleshipping_shippingAddress_addressFields_isValidated': 'true',
        'dwfrm_singleshipping_shippingAddress_addressFields_firstName': accountDict['first_name'],
        'dwfrm_singleshipping_shippingAddress_addressFields_lastName': accountDict['last_name'],
        'dwfrm_singleshipping_shippingAddress_addressFields_title': 'Mr',
        'dwfrm_singleshipping_shippingAddress_addressFields_birthdayfields_day': day,
        'dwfrm_singleshipping_shippingAddress_addressFields_birthdayfields_month': month,
        'dwfrm_singleshipping_shippingAddress_addressFields_birthdayfields_year': year,
        'dwfrm_singleshipping_shippingAddress_addressFields_birthday': birthday,
        'dwfrm_singleshipping_shippingAddress_addressFields_address1': accountDict['address'],
        'dwfrm_singleshipping_shippingAddress_addressFields_postal': accountDict['zipcode'],
        'dwfrm_singleshipping_shippingAddress_addressFields_city': accountDict['city'],
        'dwfrm_singleshipping_shippingAddress_addressFields_states_state': accountDict['province'],
        'dwfrm_singleshipping_shippingAddress_addressFields_country': accountDict['country'],
        'dwfrm_singleshipping_shippingAddress_useAsBillingAddress': 'true',
        'dwfrm_singleshipping_shippingAddress_shippingMethodID': 'ANY_STD',
        'dwfrm_singleshipping_shippingAddress_save': save,
        'csrf_token':token
    }

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[AWLAB] ' + utility.threadTime(mode) + 'Checking out..')

    while True:

        try:
            r = session.post(shipping_link, data=fatturazione_payload, proxies=proxy, allow_redirects=True)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '429':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed setting shipping address, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed setting shipping address, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed setting shipping address, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed setting shipping address, retrying..')
            time.sleep(delay)
            continue

        if 'carrello' in r.url or 'cart' in r.url:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [OOS] Failed setting shipping address, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.url) + '] [ERROR] [OOS] Failed setting shipping address, retrying..')
            time.sleep(delay)
            continue
        elif 'fatturazione' not in r.url and 'billing' not in r.url:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [CSV] Failed setting shipping address, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.url) + '] [ERROR] [CSV] Failed setting shipping address, retrying..')
            time.sleep(delay)
            continue
        else:
            break

    return proxy

def SetCoupon(session, coupon, token, mode, accountDict, country, prx):
    
    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Submitting coupon..' + utility.bcolors.ENDC)
    logging.info('[AWLAB] ' + utility.threadTime(mode) + 'Submitting coupon..')

    if 'IT' in country:
        applyCoupon = 'Applica'
        referer = 'https://www.aw-lab.com/billing'
        cpn_link = 'https://www.aw-lab.com/on/demandware.store/Sites-awlab-'+country.lower()+'-Site/'+country.lower()+'_'+country+'/COBilling-Billing'
    elif 'ES' in country:
        applyCoupon = 'aplicar'
        referer = 'https://'+country.lower()+'.aw-lab.com/billing'
        cpn_link = 'https://'+country.lower()+'.aw-lab.com/on/demandware.store/Sites-awlab-'+country.lower()+'-Site/'+country.lower()+'_'+country+'/COBilling-Billing'
    else:
        applyCoupon = 'Apply'
        referer = 'https://en.aw-lab.com/billing'
        cpn_link = 'https://en.aw-lab.com/on/demandware.store/Sites-awlab-en-Site/en_'+country+'/COBilling-Billing'

    coupon_data = {
        'dwfrm_billing_save': 'true',
        'dwfrm_billing_billingAddress_addressId': 'guest-shipping',
        'dwfrm_billing_billingAddress_addressFields_isValidated': 'true',
        'dwfrm_billing_billingAddress_addressFields_firstName': accountDict['first_name'],
        'dwfrm_billing_billingAddress_addressFields_lastName': accountDict['last_name'],
        'dwfrm_billing_billingAddress_addressFields_address1': accountDict['address'],
        'dwfrm_billing_billingAddress_addressFields_postal': accountDict['zipcode'],
        'dwfrm_billing_billingAddress_addressFields_city': accountDict['city'],
        'dwfrm_billing_billingAddress_addressFields_states_state': accountDict['province'],
        'dwfrm_billing_billingAddress_addressFields_country': accountDict['country'],
        'dwfrm_billing_billingAddress_invoice_accountType': 'private',
        'dwfrm_billing_billingAddress_invoice_companyName': '',
        'dwfrm_billing_billingAddress_invoice_taxNumber': '',
        'dwfrm_billing_billingAddress_invoice_vatNumber': '',
        'dwfrm_billing_billingAddress_invoice_sdlCode': '',
        'dwfrm_billing_billingAddress_invoice_pec': '',
        'dwfrm_billing_couponCode': coupon,
        'dwfrm_billing_applyCoupon': applyCoupon,
        'dwfrm_billing_paymentMethods_creditCard_encrypteddata': '',
        'dwfrm_billing_paymentMethods_creditCard_type': '',
        'dwfrm_adyPaydata_brandCode': '',
        'noPaymentNeeded': 'true',
        'dwfrm_billing_paymentMethods_creditCard_selectedCardID': '',
        'dwfrm_billing_paymentMethods_selectedPaymentMethodID': 'PayPal',
        'dwfrm_billing_billingAddress_personalData': 'true',
        'dwfrm_billing_billingAddress_tersmsOfSale': 'true',
        'csrf_token': token
    }

    headerCF = dict(session.headers)
    headerCF.update({'referer': referer})
    headerCF.update({'x-requested-with': 'XMLHttpRequest'})

    while True:

        try:
            r = session.post(cpn_link, data = coupon_data, headers=headerCF, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '429':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed submitting coupon, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed submitting coupon, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed submitting coupon, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed submitting coupon, retrying..')
            time.sleep(delay)
            continue
        
        break

    return proxy

def GetEncyptCreditCard(accountDict, mode):

    while True:
        
        try:
            cse = ClientSideEncrypter(PUB_EXPONENT + "|" + MODULUS)
            adyen_nonce = cse.generate_adyen_nonce(accountDict['holder_name'], accountDict['credit_card'], accountDict['cvv'], accountDict['month'], accountDict['year'])
            break
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting Credit Card info, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting Credit Card info, retrying..')
            time.sleep(delay)
            continue
    
    return adyen_nonce

def PaymentForm(session, payment, token, accountDict, mode, captchaEnabled, country, prx):

    if 'IT' in country:
        referer = 'https://www.aw-lab.com/billing'
        billing_link = 'https://www.aw-lab.com/on/demandware.store/Sites-awlab-'+country.lower()+'-Site/'+country.lower()+'_'+country+'/COBilling-Billing'
    elif 'ES' in country:
        referer = 'https://'+country.lower()+'.aw-lab.com/billing'
        billing_link = 'https://'+country.lower()+'.aw-lab.com/on/demandware.store/Sites-awlab-'+country.lower()+'-Site/'+country.lower()+'_'+country+'/COBilling-Billing'
    else:
        referer = 'https://en.aw-lab.com/billing'
        billing_link = 'https://en.aw-lab.com/on/demandware.store/Sites-awlab-en-Site/en_'+country+'/COBilling-Billing'

    # ---------------------------------------------------------------------------------- #
    headerCF = dict(session.headers)
    headerCF.update({'referer': referer})
    headerCF.update({'x-requested-with': 'XMLHttpRequest'})
    # ---------------------------------------------------------------------------------- #

    cardType = ''
    captcha = ''
    adyen = ''
    proxy = prx

    if 'CAD' in payment:
        paymentMethod = 'CASH_ON_DELIVERY'
    elif 'CC' in payment:
        paymentMethod = 'CREDIT_CARD'
        adyen = GetEncyptCreditCard(accountDict, mode)

        if accountDict['credit_card'][0] == '5':
            cardType = 'mc'
        else:
            cardType = 'visa'
    else:
        paymentMethod = 'PayPal'

    ordine_payload = {
        'dwfrm_billing_save': 'true',
        'dwfrm_billing_billingAddress_addressId': 'guest-shipping',
        'dwfrm_billing_billingAddress_addressFields_isValidated': 'true',
        'dwfrm_billing_billingAddress_addressFields_firstName': accountDict['first_name'],
        'dwfrm_billing_billingAddress_addressFields_lastName': accountDict['last_name'],
        'dwfrm_billing_billingAddress_addressFields_address1': accountDict['address'],
        'dwfrm_billing_billingAddress_addressFields_postal': accountDict['zipcode'],
        'dwfrm_billing_billingAddress_addressFields_city': accountDict['city'],
        'dwfrm_billing_billingAddress_addressFields_states_state': accountDict['province'],
        'dwfrm_billing_billingAddress_addressFields_country': accountDict['country'],
        'dwfrm_billing_billingAddress_invoice_accountType': 'private',
        'dwfrm_billing_billingAddress_invoice_companyName': '',
        'dwfrm_billing_billingAddress_invoice_taxNumber': '',
        'dwfrm_billing_billingAddress_invoice_vatNumber': '',
        'dwfrm_billing_billingAddress_invoice_sdlCode': '',
        'dwfrm_billing_billingAddress_invoice_pec': '',
        'dwfrm_billing_couponCode': '',
        'dwfrm_billing_paymentMethods_selectedPaymentMethodID': paymentMethod,
        'dwfrm_billing_paymentMethods_creditCard_encrypteddata': adyen,
        'dwfrm_billing_paymentMethods_creditCard_type': cardType,
        'dwfrm_adyPaydata_brandCode': '',
        'noPaymentNeeded': 'true',
        'dwfrm_billing_paymentMethods_creditCard_selectedCardID': '',
        'g-recaptcha-response': captcha,
        'dwfrm_billing_billingAddress_personalData': 'true',
        'dwfrm_billing_billingAddress_tersmsOfSale': 'true',
        'csrf_token': token
    }

    while True:
        
        '''
        if captchaEnabled:

            print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Waiting for captcha..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + 'Waiting for captcha..')

            while True:
                try:
                    # block until we get sent a captcha token and repeat
                    captcha = tokens.get()
                    print(utility.threadTime(mode) + utility.bcolors.OKGREEN + 'Successfully got captcha token!' + utility.bcolors.ENDC)
                    logging.info('[AWLAB] ' + utility.threadTime(mode) + 'Successfully got captcha token!')
                    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Completing checkout..' + utility.bcolors.ENDC)
                    logging.info('[AWLAB] ' + utility.threadTime(mode) + 'Completing checkout..')
                    print(captcha)
                    ordine_payload.update({'g-recaptcha-response':captcha})
                    break
                except Exception:
                    continue
        '''

        try:
            r = session.post(billing_link, headers=headerCF, allow_redirects=True, data=ordine_payload, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '429':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[RATE LIMIT] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [RATE LIMIT] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            if str(r.status_code) == '502':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[BAD GATEWAY] Website connection lost, retrying..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [BAD GATEWAY] Website connection lost, retrying..')
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        if 'CASH_ON_DELIVERY' in paymentMethod:

            try:
                soup = BeautifulSoup(r.text, 'html.parser')

                checkout = str(soup.find('span', {'class':'b-checkout-confirmation__order-number'})).split('<span>')[1].split('</span>')[0]

                print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + checkout + '] [' + str(r.status_code) + '] Successfully checked out!')
                setTitle(1)
                break
            except Exception as e:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting order number, retrying..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting order number, retrying..')
                time.sleep(delay)
                continue

        elif 'PayPal' in paymentMethod:

            try:
                token = str(r.url).split('token=')[1].split('&')[0]
                checkout = 'https://www.paypal.com/webscr?cmd=_express-checkout&token='+token
                print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + checkout + '] [' + str(r.status_code) + '] Successfully checked out!')
                setTitle(1)
                break

            except Exception as e:
                if str(r.url) == 'https://www.aw-lab.com/carrello' or str(r.url) == 'https://es.aw-lab.com/cart' or str(r.url) == 'https://en.aw-lab.com/cart':
                    print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Checkout blocked, rejected the request retrying..' + utility.bcolors.ENDC)
                    logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Checkout blocked, rejected the request retrying..')
                    time.sleep(delay)
                    continue
                else:
                    print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
                    logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting PayPal link, retrying..')
                    time.sleep(delay)
                    continue
                
        else:
            
            if 'Adyen' in r.url:
                checkout = str(r.url)
                print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + checkout + '] [' + str(r.status_code) + '] Successfully checked out!')
                setTitle(1)
                break

            elif 'carrello' in r.url or 'cart' in r.url:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Checkout blocked, rejected the request retrying..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[ERROR] Checkout blocked, rejected the request retrying..')
                time.sleep(delay)
                continue

            elif 'revieworder' in r.url or 'riepilogoordine' in r.url or 'ordineconfermato' in r.url or 'orderconfirmed' in r.url:

                try:
                    soup = BeautifulSoup(r.text, 'html.parser')

                    checkout = str(soup.find('span', {'class':'b-checkout-confirmation__order-number'})).split('<span>')[1].split('</span>')[0]

                    print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
                    logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + checkout + '] [' + str(r.status_code) + '] Successfully checked out!')
                    setTitle(1)
                    break
                except:
                    print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Payment declined, retrying..' + utility.bcolors.ENDC)
                    logging.info('[AWLAB] ' + utility.threadTime(mode) + '[ERROR] Payment declined, retrying..')
                    adyen = GetEncyptCreditCard(accountDict, mode)
                    time.sleep(delay)
                    continue

            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting checkout link, retrying..' + utility.bcolors.ENDC)
                logging.info('[AWLAB] ' + utility.threadTime(mode) + '[ERROR] Failed getting checkout link, retrying..')
                time.sleep(delay)
                continue
    
    return checkout

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


def main(pid, size, payment, coupon, mode, accountDict):

    SetupCloudscraper()
    
    prx = GetNewProxy()

    country = accountDict['country']

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

    if 'ATC' not in mode:
        while True:
            sizeDict, prx = CheckProductInfo(s, pid, payment, country, prx)
            variant, sizeID = utility.SelectSize(sizeDict, size, payment, 'AWLAB', configDict)

            if variant != -1 and sizeID != -1:            
                break
    else:
        variant = pid
        sizeID = pid.split('_')[3]

    start_time = datetime.now()
    
    print(utility.threadTime(payment) + utility.bcolors.WARNING + 'Adding to cart size: ['+sizeID+']' + utility.bcolors.ENDC)
    logging.info('[AWLAB] ' + utility.threadTime(payment) + 'Adding to cart size: ['+sizeID+']')
    productURL, productName, productIMG, prx = AddToCart(s, variant, payment, country, prx)

    token, phone_code, prx = GetCheckoutToken(s, payment, country, prx)
    prx = StartCheckout(s, token, accountDict, payment, phone_code, country, prx)

    if coupon != '':
        prx = SetCoupon(s, coupon, token, payment, accountDict, country, prx)

    checkout = PaymentForm(s, payment, token, accountDict, payment, True, country, prx)
    
    final_time = datetime.now()-start_time
    
    if 'IT' in country:
        defaultURL = 'https://www.aw-lab.com/'
    elif 'ES' in country:
        defaultURL = 'https://es.aw-lab.com/'
    else:
        defaultURL = 'https://en.aw-lab.com/'

    if 'https' in checkout:
        try:
            checkout = utility.getCheckoutLink(s, defaultURL, checkout)
        except Exception as e:
            print(utility.threadTime(payment) + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
            logging.info('[AWLAB] ' + utility.threadTime(payment) + '[' + str(e) + '] Failed getting checkout link with cookie!')
            time.sleep(100)

    if 'CAD' in payment:
        payment = 'Cash on delivery'
    elif 'CC' in payment:
        payment = 'Credit Card'
    else:
        payment = 'PayPal'

    crissWebhook.sendAWLABWebhook('AW-LAB '+country, productURL, accountDict.get('email'), productName, sizeID, checkout, coupon, productIMG, payment, str(final_time), mode)
    crissWebhook.publicAWLABWebhook('AW-LAB '+country, productURL, productName, sizeID, productIMG, str(final_time), payment, mode)
    crissWebhook.staffAWLABWebhook('AW-LAB '+country, productName, sizeID, productIMG, str(final_time), mode)

    input('')
    time.sleep(100)

def shockdrop(URL, val, mode):

    title = utility.getTitleHeader() + "  -  AWLAB  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    accountDict = {}

    try:
        global allProxies
        allProxies = utility.loadProxies('aw-lab')
        with open('aw-lab/task.csv', 'r') as csv_file:
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
                    
                    coupon = line['COUPON']

                    accountDict = {
                        'email':email,
                        'first_name':name,
                        'last_name':line['LAST NAME'],
                        'phone_number':phone_number,
                        'address':line['ADDRESS'],
                        'zipcode':line['ZIPCODE'],
                        'city':line['CITY'],
                        'province':line['PROVINCE'],
                        'country':line['COUNTRY'],
                        'holder_name':line['HOLDER NAME'],
                        'credit_card':line['CARD NUMBER'],
                        'month':line['EXP MONTH'],
                        'year':line['EXP YEAR'],
                        'cvv':line['CVV']
                    }

                    break

                except Exception as e:
                    print(utility.threadTime(mode) + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                    logging.info('[AWLAB] ' + utility.threadTime(mode) + '[' + str(e) + '] Failed loading task, please check csv file!')
                    input('Press ENTER to exit.')
                    sys.exit()

            if 'https://www.' in URL or 'https://en.' in URL or 'https://es.' in URL:
                    mode2 = 'Direct URL'
            else:
                checkMode = URL.split('_')
                if len(checkMode) == 4:
                    mode2 = 'Direct ATC'
                else:
                    mode2 = 'PID'

            for _ in range(0, val):
                t = Thread(target=main, args=(URL, 'RANDOM', mode, coupon, mode2, accountDict))
                t.start()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[AWLAB] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()
    
def start_main():

    title = utility.getTitleHeader() + "  -  AWLAB  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    '''
    global harvester
    server_thread = Thread(target=harvester.serve, daemon=True)
    server_thread.start()
    # launch a browser instance where we can solve the captchas
    harvester.launch_browser()
    '''

    try:
        global allProxies
        allProxies = utility.loadProxies('aw-lab')
        with open('aw-lab/task.csv', 'r') as csv_file:
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
                        'first_name':name,
                        'last_name':line['LAST NAME'],
                        'phone_number':phone_number,
                        'address':line['ADDRESS'],
                        'zipcode':line['ZIPCODE'],
                        'city':line['CITY'],
                        'province':line['PROVINCE'],
                        'country':line['COUNTRY'],
                        'holder_name':line['HOLDER NAME'],
                        'credit_card':line['CARD NUMBER'],
                        'month':line['EXP MONTH'],
                        'year':line['EXP YEAR'],
                        'cvv':line['CVV']
                    }

                except Exception as e:
                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                    logging.info('[AWLAB] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                    input('Press ENTER to exit.')
                    sys.exit()
                
                if(line['PAYMENT'] == 'PP') or (line['PAYMENT'] == 'CAD') or (line['PAYMENT'] == 'CC'):

                    if 'https://www.' in line['PRODUCT'] or 'https://en.' in line['PRODUCT'] or 'https://es.' in line['PRODUCT']:
                            mode = 'Direct URL'
                    else:
                        checkMode = line['PRODUCT'].split('_')
                        if len(checkMode) == 4:
                            mode = 'Direct ATC'
                        else:
                            mode = 'PID'

                    t = Thread(target=main, args=(line['PRODUCT'], line['SIZE'], line['PAYMENT'], line['COUPON'], mode, accountDict))
                    t.start()
                else:
                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check payment method!' + utility.bcolors.ENDC)
                    logging.info('[AWLAB] ' + utility.threadTime('') + '[' + line['PAYMENT'] + '] Failed loading task, please check payment method!')
                    input('Press ENTER to exit.')
                    sys.exit()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[AWLAB] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit()

if __name__ == '__main__':
    start_main() 