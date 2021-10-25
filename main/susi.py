# -*- coding: utf-8 -*-
#!/bin/env python

''' SUSI '''

import os, sys, requests, json, random, csv, time, crissWebhook, utility
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from os import system
from threading import Thread, Lock


def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[SUSI] ' + utility.threadTime('') + str(exc_value))
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
    

    title = utility.getTitleHeader() + "  -  Susi  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()


headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.26',
    'content-type': 'application/x-www-form-urlencoded'
}

headersXML = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.26',
    'x-requested-with':'XMLHttpRequest'
}

headersXMLTemp = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.26',
    'x-requested-with':'XMLHttpRequest',
    'content-type': 'application/x-www-form-urlencoded'
}

def ScrapeProduct(session, url, prx):

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
    logging.info('[SUSI] ' + utility.threadTime('') + 'Getting product info..')

    productTitle = ''
    sizeDict = {}
    sizeID = ''
    proxy = prx

    while True:

        try:
            r = session.get(url, headers=headers, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        
        try:
            productIMG = 'https://www.susi.it' + str(soup.find('img', {'class':'primary-image'})['src'])

            productTitle = soup.find('h2', {'class':'product-name'}).text 

            if(productTitle == ""):
                productTitle = soup.find('div', {'class','label'}).text.split(': ')[1]
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [PRODUCT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [PRODUCT] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        
        try:
            hrefs = soup.find_all('a', {'class':'swatchanchor'})

            if  len(hrefs) == 0:
                print(utility.threadTime('') + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                logging.info('[SUSI] ' + utility.threadTime('') + 'Product out of stock, retrying..')
                time.sleep(delay)
                continue
            else:
                for sizes in hrefs:
                    try:
                        r = session.get(sizes['href'] + '&Quantity=1&format=ajax&productlistid=undefined', headers=headersXML)

                        if str(r.status_code) == '503':
                            print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                            proxy = GetNewProxy()
                            time.sleep(delay)
                            continue
                
                        soup = BeautifulSoup(r.text, 'html.parser')

                        productID = soup.find('span', {'itemprop':'productID'}).text
                        sizeID = str(sizes.text).replace('\n', '')

                        if sizeID != '':
                            sizeDict.update({productID:sizeID})
                    except:
                        pass

                break

        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [SIZES] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [SIZES] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

    return productTitle, productIMG, sizeDict, proxy

def AddToCart(session, pid, prx):

    atc_payload = {
        'Quantity': '1',
        'cartAction': 'add',
        'pid': pid
    }

    proxy = prx

    while True:

        try:
            r = session.post('https://www.susi.it/on/demandware.store/Sites-susi-Site/it_IT/Cart-AddProduct?format=ajax', headers=headersXMLTemp, data=atc_payload, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        

        try:
            checkCart = str(soup.find('span', {'class':'minicart-quantity'}).text).replace('\n','')
            
            if '0' in checkCart:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[SUSI] ' + utility.threadTime('') + '[ERROR] Failed adding to cart, retrying..')
                time.sleep(delay)
                continue
            else:
                checkCart2 = str(soup.find('ul', {'class':'product-availability-list'}).text)
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Product carted but out of stock, trying checkout..' + utility.bcolors.ENDC)
                logging.info('[SUSI] ' + utility.threadTime('') + '[ERROR] ['+checkCart2+'] Product carted but out of stock, trying checkout..')
                #qui potremmo provare a rimuoverle e provare un'altra size
                break
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully added to cart!')
            setTitle(0)
            break

    return proxy
       
'''
def removeCart(session):

    remove_payload = {
        'dwfrm_cart_shipments_i0_items_i0_deleteProduct': 'Rimuovi',
        'dwfrm_cart_updateCart': 'dwfrm_cart_updateCart',
        'dwfrm_cart_couponCode': '',
        'csrf_token': ''
    }

    while True:

        try:
            r = session.get('https://www.susi.it/it-IT/carrello/', headers=headers)

            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            token = str(soup.find('input', {'name':'csrf_token'})['value'])

            remove_payload.update({'csrf_token':token})

            r = session.post('https://www.susi.it/on/demandware.store/Sites-susi-Site/it_IT/Cart-SubmitForm', headers=headersXMLTemp, data=remove_payload, proxies=proxy)

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
'''

def CheckoutToken(session, accountDict, prx):

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Getting checkout token..' + utility.bcolors.ENDC)
    logging.info('[SUSI] ' + utility.threadTime('') + 'Getting checkout token..')

    proxy = prx

    while True:
        
        try:
            r = session.get('https://www.susi.it/it-IT/carrello/', headers=headers, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:         
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting checkout token, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting checkout token, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting checkout token, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting checkout token, retrying..')
            time.sleep(delay)
            continue

        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            token = soup.find('input', {'name':'csrf_token'})['value']
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully got checkout token!' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully got checkout token!')
            break
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting checkout token, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting checkout token, retrying..')
            time.sleep(delay)
            continue
    
    return token, proxy

def Checkout(session, token, accountDict, prx):

    fatturazione_payload = {
        'dwfrm_singleshipping_shippingAddress_addressFields_firstName': accountDict.get('name'),
        'dwfrm_singleshipping_shippingAddress_addressFields_lastName': accountDict.get('last name'),
        'dwfrm_singleshipping_shippingAddress_addressFields_address1': accountDict.get('address'),
        'dwfrm_singleshipping_shippingAddress_addressFields_address2': accountDict.get('address_2'),
        'dwfrm_singleshipping_shippingAddress_addressFields_postal': accountDict.get('zipcode'),
        'dwfrm_singleshipping_shippingAddress_addressFields_city': accountDict.get('city'),
        'dwfrm_singleshipping_shippingAddress_addressFields_phone': accountDict.get('phone number'),
        'dwfrm_singleshipping_shippingAddress_addressFields_country': accountDict.get('country'),
        'dwfrm_singleshipping_shippingAddress_addressFields_states_state': accountDict.get('province'),
        'dwfrm_singleshipping_shippingAddress_useAsBillingAddress': 'true',
        'dwfrm_singleshipping_shippingAddress_shippingMethodID': 'DHL-Express',
        'dwfrm_singleshipping_shippingAddress_save': 'Passa a Fatturazione >',
        'csrf_token':token
    }

    print(utility.threadTime('') + utility.bcolors.WARNING +  'Checking out..' + utility.bcolors.ENDC)
    logging.info('[SUSI] ' + utility.threadTime('') + 'Checking out..')

    proxy = prx

    ''' FATTURAZIONE '''
    while True:

        try:
            r = session.post('Https://www.susi.it/it-IT/cliente/fatturazione/', headers=headersXMLTemp, data=fatturazione_payload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        
        try:
            if 'Passa a Invia ordine' in str(r.text):
                break
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [FATTURAZIONE] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [FATTURAZIONE] Failed checking out, retrying..')
            time.sleep(delay)
            continue

    ordine_payload = {
        'dwfrm_billing_save': 'true',
        'dwfrm_billing_billingAddress_addressFields_firstName': accountDict.get('name'),
        'dwfrm_billing_billingAddress_addressFields_lastName': accountDict.get('last name'),
        'dwfrm_billing_billingAddress_addressFields_address1': accountDict.get('address'),
        'dwfrm_billing_billingAddress_addressFields_address2': accountDict.get('address_2'),
        'dwfrm_billing_billingAddress_addressFields_postal': accountDict.get('zipcode'),
        'dwfrm_billing_billingAddress_addressFields_city': accountDict.get('city'),
        'dwfrm_billing_billingAddress_addressFields_country': accountDict.get('country'),
        'dwfrm_billing_billingAddress_addressFields_states_state': accountDict.get('province'),
        'dwfrm_billing_billingAddress_addressFields_phone': accountDict.get('phone number'),
        'dwfrm_billing_billingAddress_email_emailAddress': accountDict.get('email'),
        'dwfrm_billing_billingAddress_acceptPrivacy': 'true',
        'dwfrm_billing_couponCode': '',
        'dwfrm_billing_giftCertCode': '',
        'dwfrm_billing_paymentMethods_selectedPaymentMethodID': 'paypal_pro',
        'dwfrm_billing_paymentMethods_bml_year': '',
        'dwfrm_billing_paymentMethods_bml_month':'' ,
        'dwfrm_billing_paymentMethods_bml_day': '',
        'dwfrm_billing_paymentMethods_bml_ssn': '',
        'dwfrm_billing_save': 'Passa a Invia ordine >',
        'csrf_token':token
    }

    ''' RIEPILOGO ORDINE '''
    while True:

        try:
            r = session.post('https://www.susi.it/it-IT/cliente/riepilogo-ordine/', headers=headers, data=ordine_payload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed checking out, retrgying..')
            time.sleep(delay)
            continue

        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            ordine = soup.find('input', {'name':'invoice'})['value']
            subtotal = soup.find('tr', {'class':'order-subtotal'}).encode('utf-8')
            subtotal = str(subtotal).split('xac')[1].split('</')[0].replace(',', '.').replace(' ', '')
            break
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [LAST STEP] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [LAST STEP] Failed checking out, retrgying..')
            time.sleep(delay)
            continue

    return ordine, subtotal, proxy

def GetPayPal(session, ordine, subtotal, accountDict, prx):

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Getting PayPal link..' + utility.bcolors.ENDC)
    logging.info('[SUSI] ' + utility.threadTime('') + 'Getting PayPal link..')
        
    headersPayPal = {
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.26',
        'origin':'https://www.paypal.com',
        'content-type': 'application/x-www-form-urlencoded'
    }

    pp_payload = {
        'amount': subtotal,
        'shipping': '0.00',
        'handling': '0.00',
        'tax': '0',
        'business': 'amministrazione.web@susi.it',
        'notify_url': 'https://www.susi.it/on/demandware.store/Sites-susi-Site/it_IT/PayPalPro-Notify?ref=' + str(ordine),
        'currency_code': 'EUR',
        'lc': 'IT',
        'return': 'https://www.susi.it/on/demandware.store/Sites-susi-Site/it_IT/PayPalPro-Success?ref=' + str(ordine),
        'cancel_return': 'https://www.susi.it/on/demandware.store/Sites-susi-Site/it_IT/PayPalPro-Cancel?ref=' + str(ordine),
        'address1': accountDict.get('address'),
        'city': accountDict.get('city'),
        'state': accountDict.get('province'),
        'country': accountDict.get('country'),
        'first_name':accountDict.get('name'),
        'last_name':accountDict.get('last name'),
        'night_phone_b': accountDict.get('phone number'),
        'zip': accountDict.get('zipcode'),
        'paymentaction': 'sale',
        'billing_address1': accountDict.get('address'),
        'billing_city': accountDict.get('city'),
        'billing_state': accountDict.get('province'),
        'billing_country': accountDict.get('country'),
        'billing_zip':accountDict.get('zipcode'),
        'invoice': ordine,
        'billing_first_name': accountDict.get('name'),
        'billing_last_name':  accountDict.get('last name'),
        'address_override': '1',
        'rm': '2',
        'no_shipping': '0'
    }

    proxy = prx
    
    while True:
    
        try:
            r = session.post('https://www.paypal.com/cgi-bin/webscr?cmd=_hssnode-merchantpaymentweb', headers=headersPayPal, data=pp_payload, allow_redirects=True, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting PayPal link, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting PayPal link, retrgying..')
            time.sleep(delay)
            continue
    
        if 'paypal' in r.url:
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!'  + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully checked out!')
            setTitle(1)
            break
        else:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting PayPal link, retrgying..')
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

def main(link, size, accountDict):

    prx = GetNewProxy()
    s = requests.session()

    while True:
        productTitle, productIMG, sizeDict, prx = ScrapeProduct(s, link, prx)
        pid, sizeID = utility.SelectSize(sizeDict, size, '', 'SUSI', configDict)

        if pid != -1 and sizeID != 1:
            break;

    start_time = datetime.now()

    print(utility.threadTime('') + utility.bcolors.WARNING +  'Adding to cart size: [' + sizeID + ']' + utility.bcolors.ENDC)
    logging.info('[SUSI] ' + utility.threadTime('') + 'Adding to cart size: [' + sizeID + ']')
    prx = AddToCart(s, pid, prx)
    token, prx = CheckoutToken(s, accountDict, prx)
    ordine, subtotal, prx = Checkout(s, token, accountDict, prx)
    checkoutLink = GetPayPal(s, ordine, subtotal, accountDict, prx)

    final_time = datetime.now()-start_time

    try:
        checkout_link = utility.getCheckoutLink(s, 'https://www.paypal.com/', checkoutLink)
    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
        logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + ']Failed getting checkout link with cookie!')
        time.sleep(1000)

    crissWebhook.sendWebhook('Susi', link, accountDict.get('email'), productTitle, sizeID, checkout_link, productIMG, 'PayPal', str(final_time))
    crissWebhook.publicWebhook('Susi', link, productTitle, sizeID, productIMG, str(final_time), 'PayPal')
    crissWebhook.staffWebhook('Susi', productTitle, sizeID, productIMG, str(final_time))

    input('')
    time.sleep(2000)

def shockdrop(URL, val):

    title = utility.getTitleHeader() + "  -  Susi  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    accountDict = {}

    try:
        global allProxies 
        allProxies = utility.loadProxies('susi')
        with open('susi/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:

                try:
                    email = line['EMAIL']
                    name = line['FIRST NAME']
                    if('RANDOM' in email):
                        if('RANDOM' in line['FIRST NAME']):
                            name, email = utility.getCathcallEMail(line['LAST NAME'], email.replace('RANDOM', ''))
                    phone_number = line['PHONE']
                    if('RANDOM' in phone_number):
                        phone_number = utility.getRandomNumber()
                    accountDict = {
                        'email': email,
                        'name':name,
                        'last name':line['LAST NAME'],
                        'address':line['ADDRESS'],
                        'address_2':line['ADDRESS 2'],
                        'city':line['CITY'],
                        'zipcode':line['ZIPCODE'],
                        'phone number':phone_number,
                        'province':line['PROVINCE'],
                        'country':line['COUNTRY']
                    }

                    break

                except Exception as e:
                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                    logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                    input('Press ENTER to exit.')
                    sys.exit()

        for tasks in range(0, val):
            t =Thread(target=main, args=(URL, 'RANDOM', accountDict))
            t.start()

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)

def start_main():

    title = utility.getTitleHeader() + "  -  Susi  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies 
        allProxies = utility.loadProxies('susi')
        with open('susi/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:

                try:
                    email = line['EMAIL']
                    name = line['FIRST NAME']
                    if('RANDOM' in email):
                        if('RANDOM' in line['FIRST NAME']):
                            name, email = utility.getCathcallEMail(line['LAST NAME'], email.replace('RANDOM', ''))
                    phone_number = line['PHONE']
                    if('RANDOM' in phone_number):
                        phone_number = utility.getRandomNumber()
                    accountDict = {
                        'email': email,
                        'name':name,
                        'last name':line['LAST NAME'],
                        'address':line['ADDRESS'],
                        'address_2':line['ADDRESS 2'],
                        'city':line['CITY'],
                        'zipcode':line['ZIPCODE'],
                        'phone number':phone_number,
                        'province':line['PROVINCE'],
                        'country':line['COUNTRY']
                    }

                except Exception as e:
                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                    logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                    input('Press ENTER to exit.')
                    sys.exit(-1)

                t = Thread(target=main, args=(line['URL'], line['SIZE'], accountDict))
                t.start()
                
    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[SUSI] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)

if __name__ == '__main__':
    start_main() 