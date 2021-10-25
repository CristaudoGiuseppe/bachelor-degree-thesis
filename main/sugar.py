# -*- coding: utf-8 -*-
#!/bin/env python

''' SUGAR '''

import requests, signal, json, random, csv, time, sys, re, os, utility, crissWebhook
import cfscrape, cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import logging
from threading import Thread, Lock
from os import system

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[SUGAR] ' + utility.threadTime('') + str(exc_value))
    input("Press ENTER to exit.")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

os.chdir(os.path.dirname(sys.executable))
configDict = utility.getDictConfig()
delay = float(configDict.get('delay'))
all_proxies = None
proxy = None

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
    

    title = utility.getTitleHeader() + "  -  Sugar  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()

headers = {
      'authority': 'www.sugar.it',
      'Cache-Control': 'no-cache, no-store',
      'Pragma': 'no-cache',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
}

headersXML = {
      'authority': 'www.sugar.it',
      'x-requested-with': 'XMLHttpRequest',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
}

def ScrapeProduct(session, url, prx):

      sizeDict = {}
      idDict = {}
      proxy = prx

      print(utility.threadTime('') + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
      logging.info('[SUGAR] ' + utility.threadTime('') + 'Getting product info..')

      while True:

            try:
                  r = session.get(url, headers=headers, proxies=proxy)

                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue
                  
                  soup = BeautifulSoup(r.text, 'html.parser')

            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue

            try:
                  img = soup.find('img', {'class':'box1'})['src']
            except:
                  img = ''
                  
            try:
                  title = soup.find('span', {'class':'base'}).text
                  atc_link = soup.find('form', {'id':'product_addtocart_form'})['action']
                  form_key = soup.find('input', {'name':'form_key'})['value']
                  product  = soup.find('input', {'name':'product'})['value']

            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [PULLED] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [PULLED] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue
            
            try:
                  size_info = str(r.text).split('"spConfig": ')[1].split(',"template"')[0] +'}'
                  super_attribute = str(size_info).split('"id":"')[1].split('"')[0]

                  for id in json.loads(size_info)['attributes'][super_attribute]['options']:
                        if id['products'] != []:
                              sizeDict.update({id['products'][0]:str(id['label']).replace('\u00bd','.5')})
                              idDict.update({str(id['label']).replace('\u00bd','.5'):id['id']})
                  
                  if len(sizeDict) == 0:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                        logging.info('[SUGAR] ' + utility.threadTime('') + 'Product out of stock, retrying..')
                        time.sleep(delay)
                        continue
                  else:
                        break
            
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [SIZES] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [SIZES] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue
      
      return atc_link, product, super_attribute, sizeDict, idDict, title, form_key, img, proxy
       
def Login(s, username, password, prx):

      proxy = prx

      print(utility.threadTime('') + utility.bcolors.WARNING + 'Logging in with: ' + username + utility.bcolors.ENDC)
      logging.info('[SUGAR] ' + utility.threadTime('') + 'Logging in with: ' + username)

      while True:

            try:
                  r = s.get('https://www.sugar.it/customer/account/', headers=headers, allow_redirects=True, proxies=proxy)

                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue
                  
                  soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')

            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed loggin in, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed loggin in, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed loggin in, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed loggin in, retrying..')
                  time.sleep(delay)
                  continue

            try:
                  login_link = soup.find('form', {'class':'form form-login'})['action']
                  form_key = soup.find('input', {'name':'form_key'})['value']

                  break
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [FORM_KEY] Failed loggin in, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [FORM_KEY] Failed loggin in, retrying..')
                  time.sleep(delay)
                  continue

      headersContent = {
            'authority': 'www.sugar.it',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
      }

      login_payload = {
            'form_key': form_key,
            'login[username]': username,
            'login[password]': password
      }

      while True:

            try:
                  r = s.post(login_link, headers=headersContent, data=login_payload, proxies=proxy)

                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue
      
            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed loggin in, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed loggin in, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed loggin in, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed loggin in, retrying..')
                  time.sleep(delay)
                  continue

            if str(r.url) == 'https://www.sugar.it/customer/account/index/':
                  print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully logged in!' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') +  '[' + str(r.status_code) + '] Successfully logged in!')
                  break
            else:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [EMAIL/PASSWORD] Failed loggin in, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[ERROR] [EMAIL/PASSWORD] Failed loggin in, retrying..')
                  time.sleep(delay)
                  continue

      return proxy

def AddToCart(s, atc_link, form_key, product, option, super_attribute, sizeProduct, sizeDict, sizeID, prx):
      
      atc_payload = {
            'product': product,
            'selected_configurable_option': option,
            'related_product': '',
            'item': product,
            'form_key': form_key,
            'super_attribute[' + super_attribute + ']': sizeProduct,
      }

      proxy = prx

      while True:

            try:
                  r = s.post(atc_link, headers = headersXML, data = atc_payload, proxies=proxy)
                  #r = s.get('https://www.sugar.it/customer/section/load/?sections=cart%2Cmessages&force_new_section_timestamp=true&_='+str(time.time()).split('.')[0], proxies=proxy)


                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue

            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue

            if str(r.text) == '[]':
                  print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully added to cart!')
                  setTitle(0)
                  break
            else:
                  if 'Your bag is empty you better back to shopping.' in r.text:
                        variant, sizeID = random.choice(list(sizeDict.items()))
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [Bag is empty] Failed adding to cart..' + utility.bcolors.ENDC)
                        print(utility.threadTime('') + utility.bcolors.WARNING + 'Retrying with '+sizeID+'..' + utility.bcolors.ENDC)
                        logging.info('[SUGAR] ' + utility.threadTime('') + '[ERROR] [Bag is empty] Failed adding to cart, retrying with '+sizeID+'..')
                        time.sleep(delay)
                        continue
                  else:
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                        logging.info('[SUGAR] ' + utility.threadTime('') + '[ERROR] Failed adding to cart, retrying..')
                        time.sleep(delay)
                        continue

      return proxy, sizeID

def Checkout(s, accountDict, prx):

      proxy = prx

      print(utility.threadTime('') + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
      logging.info('[SUGAR] ' + utility.threadTime('') + 'Checking out..')

      while True:

            try:
                  r = s.get('https://www.sugar.it/paypal/express/start/', headers = headers, allow_redirects= True, proxies=proxy)

                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue
            
            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed checking out, retrgying..')
                  time.sleep(delay)
                  continue

            if 'paypal' in str(r.url):
                  print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!'  + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully checked out!')
                  setTitle(1)
                  break
            else:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.url) + '] [ERROR] Failed checking out, retrying..')
                  time.sleep(delay)
                  continue
      
      return r.url

def test():
      print('')
      """
      data = '{"addressInformation":{"shipping_address":{"customerAddressId":"73","countryId":"' + accountDict.get('country') + '","regionCode":"Bologna","region":"' + accountDict.get('province') + '","customerId":"60","street":["' + accountDict.get('address') + '"],"telephone":"' + accountDict.get('phone number') + '","postcode":"' + accountDict.get('zipcode') + '","city":"' + accountDict.get('city') + '","firstname":"Giuseppe","lastname":"Cristaudo","extension_attributes":{}},"billing_address":{"customerAddressId":"73","countryId":"IT","regionCode":"Bologna","region":"Bologna","customerId":"60","street":["Via Cogne 43"],"telephone":"3456734735","postcode":"40026","city":"Imola","firstname":"Giuseppe","lastname":"Cristaudo","saveInAddressBook":null},"shipping_method_code":"bestway","shipping_carrier_code":"tablerate"},"customerAttributes":{},"additionInformation":{"register":false,"same_as_shipping":true}}'
      
      
      while True:

            try:

                  r = s.post('https://www.sugar.it/rest/default/V1/carts/mine/checkout-information', headers = headersXML, data = data)

                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        #proxy = GetNewProxy()
                        continue

            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  #proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  #proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed setting address, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed setting address, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed setting address, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed setting address, retrying..')
                  time.sleep(delay)
                  continue

            break
      
      print('Setting payment')

      data = '{"cartId":"519","paymentMethod":{"method":"paypal_express","po_number":null,"additional_data":null}}'

      while True:

            try:

                  r = s.post('https://www.sugar.it/rest/default/V1/carts/mine/set-payment-information', headers = headersXML, data = data)

                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        #proxy = GetNewProxy()
                        continue
            
            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  #proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  #proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed setting payment, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed setting payment, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed setting payment, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed setting payment, retrying..')
                  time.sleep(delay)
                  continue
            break

      print('Checking out..')

      while True:

            try:

                  r = s.get('https://www.sugar.it/paypal/express/start/', headers = headers, allow_redirects = True)

                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        #proxy = GetNewProxy()
                        continue
            
            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  #proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  #proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed checking out, retrgying..')
                  time.sleep(delay)
                  continue

            if 'paypal' in str(r.url):
                  print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!'  + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully checked out!')
                  #setTitle(1)
                  return r.url
            else:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(r.url) + '] [ERROR] Failed checking out, retrgying..')
                  time.sleep(delay)
                  continue

      """

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

def main(url, size, accountDict):
      
      prx = GetNewProxy()
      s = requests.session()

      prx = Login(s, accountDict.get('email'), accountDict.get('psw'), prx)

      while True:
            atc_link, product, super_attribute, sizeDict, idDict, title, form_key, img_url, prx = ScrapeProduct(s, url, prx)
            variant, sizeID = utility.SelectSize(sizeDict, size, '', 'SUGAR', configDict)

            if variant != -1 and sizeID != 1:
                break;
      
      start_time = datetime.now()
      print(utility.threadTime('') + utility.bcolors.WARNING + 'Adding to cart size: [' + sizeID + ']' + utility.bcolors.ENDC)
      logging.info('[SUGAR] ' + utility.threadTime('') + 'Adding to cart size: [' + sizeID + ']')

      prx, sizeID = AddToCart(s, atc_link, form_key, product, variant, super_attribute, idDict.get(sizeID), sizeDict, sizeID, prx)

      checkout_link = Checkout(s, accountDict, prx)
      final_time = datetime.now()-start_time

      try:
            link = utility.getCheckoutLink(s, 'https://www.sugar.it/', checkout_link)
      except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
            logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] Failed getting checkout link with cookie!')
            time.sleep(100)   

      crissWebhook.sendWebhook('Sugar', url, accountDict['email'], title, sizeID, link, img_url, 'PayPal', final_time)
      crissWebhook.publicWebhook('Sugar', url, title, sizeID, img_url, final_time, 'PayPal')
      crissWebhook.staffWebhook('Sugar', title, sizeID, img_url, str(final_time))

      input('')
      time.sleep(100)

def shockdrop(URL, val):

      title = utility.getTitleHeader() + " - Sugar - Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
      utility.setTitle(title)

      try:
            global allProxies
            allProxies = utility.loadProxies('sugar')
            with open('sugar/task.csv', 'r') as csv_file:
                  csv_key = csv.DictReader(csv_file)

                  for line in csv_key:
                        try:
                              email = line['EMAIL']
                              name = line['FIRST NAME']
                              phone_number = line['PHONE']

                              
                              if 'RANDOM' in line['FIRST NAME']:
                                    utility.getName()    
                              if 'RANDOM' in phone_number:
                                    phone_number = utility.getRandomNumber()
                                    
                              accountDict = {
                                    'email': email,
                                    'psw':line['PASSWORD'],
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
                              logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                              input('Press ENTER to exit.')
                              sys.exit(-1)

                  for tasks in range(0, val):
                        t = Thread(target=main, args=(URL, 'RANDOM', accountDict))
                        t.start()

      except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
            logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
            input('Press ENTER to exit.')
            sys.exit()

def start_main():

      title = utility.getTitleHeader() + "  -  Sugar  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
      utility.setTitle(title)

      try:
            global allProxies
            allProxies = utility.loadProxies('sugar')
            with open('sugar/task.csv', 'r') as csv_file:
                  csv_key = csv.DictReader(csv_file)

                  for line in csv_key:

                        try:
                              email = line['EMAIL']
                              name = line['FIRST NAME']
                              phone_number = line['PHONE']

                        
                              if 'RANDOM' in line['FIRST NAME']:
                                    utility.getName()    
                              if 'RANDOM' in phone_number:
                                    phone_number = utility.getRandomNumber()
                              
                              accountDict = {
                                    'email': email,
                                    'psw':line['PASSWORD'],
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
                              print('caio')
                              print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                              logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                              input('Press ENTER to exit.')
                              sys.exit(-1)

                        t = Thread(target=main, args=(line['URL'], line['SIZE'], accountDict))
                        t.start()
                
      except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
            logging.info('[SUGAR] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
            input('Press ENTER to exit.')
            sys.exit(-1)

if __name__ == '__main__':
    start_main() 