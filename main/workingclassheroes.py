# -*- coding: utf-8 -*-
#!/bin/env python

import requests, time, signal, sys, json, re, csv, random, os, crissWebhook, utility, cloudscraper
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from os import system
from threading import Thread, Lock

''' WORKINGCLASSHEROES '''

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[WCH] ' + utility.threadTime('') + str(exc_value))
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
      

      title = utility.getTitleHeader() + "  -  WorkingClassHeores  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
      utility.setTitle(title)
      mutex.release()

def GetProductInfo(s, url, mode, prx):

      print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
      logging.info('[WCH] ' + utility.threadTime(mode) + ' Getting product info...')

      attributeID = None
      sizeDict = {}
      proxy = prx

      while True:

            try:
                  r = s.get(url, proxies = proxy)

                  if str(r.status_code) == '503':
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue

            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue
     
            try:
                  soup = BeautifulSoup(r.text, 'html.parser')

                  productName = str(soup).split('"name":"')[1].split('",')[0]
                  productImage = 'https://www.workingclassheroes.co.uk/images' + str(soup).split('"image":"images')[1].split('",')[0]
                  iproductID = str(soup).split('"id":')[1].split(',')[0]

                  break
            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [PRODUCT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] [PRODUCT] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue

      while True:

            headerCF = dict(s.headers)
            headerCF.update({'referer': 'https://www.workingclassheroes.co.uk/'})
            headerCF.update({'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6'})
            headerCF.update({'content-type': 'application/json; charset=UTF-8'})
            headerCF.update({'x-requested-with': 'XMLHttpRequest'})

            data = '{"controlLocation":"/modules/controls/clAttributeControl.ascx", "ProductID":"'+iproductID+'", "DetailPage":true, "dollar":0, "percentage":0}'

            try:

                  r = s.post('https://www.workingclassheroes.co.uk/wsCitrusStore.asmx/GetAttributes', headers=headerCF, data=data, proxies = proxy)
                  
                  if str(r.status_code) == '503':
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue
            
            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[ERROR] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue

            try:
                  tempJson = json.loads(r.text)
                  soup = BeautifulSoup(tempJson["d"]["HTML"],'html.parser')

                  attributeID = soup.span.input["value"]

                  for sizeItem in soup.find_all('div',{'class':'attRow'}):
                        soupSize = BeautifulSoup(str(sizeItem),'html.parser')

                        try:
                              if 'Out of stock' not in soupSize.find('span',{'class':'InStockCSS'}).text:
                                    sizeValue = str(soupSize.find('div',{'class':'name'}).text).split(',')[0].replace('UK ','')
                                    productID = soupSize.find('div',{'class':'hideme Attattributeid'}).text
                                    
                                    sizeDict.update({productID:sizeValue})
                        except:
                              pass

                  if len(sizeDict) == 0:
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + 'Product out of stock, retrying..')
                        time.sleep(delay)
                        continue
                  else:
                        if attributeID is not None:
                              break
                        else:
                              print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Product pulled, retrying..' + utility.bcolors.ENDC)
                              logging.info('[WCH] ' + utility.threadTime(mode) + '[ERROR] Product pulled, retrying..')
                              time.sleep(delay)
                              continue

            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [SIZES] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[ERROR] [SIZES] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue

      return productName, productImage, iproductID, attributeID, sizeDict, proxy         

def AddToCart(s, productID, attributeID, sizeID, url, mode, prx):

      headerCF = dict(s.headers)
      headerCF.update({'referer': url})
      headerCF.update({'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6'})
      headerCF.update({'content-type': 'application/json; charset=UTF-8'})
      headerCF.update({'x-requested-with': 'XMLHttpRequest'})

      payload = '{"iProductID":'+productID+',"iQuantity":1,"iAttributeID":'+attributeID+',"iAttributeDetailID":'+sizeID+'}'
      proxy = prx

      while True:

            try:
                  r = s.post('https://www.workingclassheroes.co.uk/wsCitrusStore.asmx/AddToBasketJSNew', data = payload, headers=headerCF, proxies = proxy)

                  if str(r.status_code) == '503':
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue
            
            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue

            if 'added to basket' in str(r.text):
                  print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully added to cart!' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '['+str(r.status_code)+'] Successfully added to cart!')
                  setTitle(0)
                  break
            else:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[ERROR] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue

      return proxy

def FirstSet(s, mode, accountDict, prx):

      headerCF = dict(s.headers)
      headerCF.update({'referer': 'https://www.workingclassheroes.co.uk/ssl/secure/'})
      headerCF.update({'content-type': 'application/json; charset=UTF-8'})
      headerCF.update({'x-requested-with': 'XMLHttpRequest'})

      payload = '{"emailAddress":"'+accountDict['email']+'" , "firstName":"'+accountDict['first_name']+'" , "lastName":"'+accountDict['last_name']+'","GDPRAllowed": false}'

      proxy = prx

      print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Setting personal info..' + utility.bcolors.ENDC)
      logging.info('[WCH] ' + utility.threadTime(mode) + ' Setting personal info..')

      while True:

            try:
                  r = s.post('https://www.workingclassheroes.co.uk/wsCitrusStore.asmx/WightCreateAnonymousCustomerLogin',  data = payload, headers=headerCF, proxies = proxy)

                  if str(r.status_code) == '503':
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue
            
            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue

            try:
                  firstJSON = json.loads(r.text)

                  if str(firstJSON['d']).split('{\"status\":')[1].split(',\"errorMsg\"')[0]:
                        print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully set personal info!' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '['+str(r.status_code)+'] Successfully set personal info!')
                        break
                  else:
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed setting personal info, retrying..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '[ERROR] ['+str(firstJSON)+'] Failed setting personal info, retrying..')
                        time.sleep(delay)
                        continue

            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed setting personal info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed setting personal info, retrying..')
                  time.sleep(delay)
                  continue
      return proxy

def SecondSet(s, mode, accountDict, prx):

      headerCF = dict(s.headers)
      headerCF.update({'referer': 'https://www.workingclassheroes.co.uk/ssl/secure/'})
      headerCF.update({'content-type': 'application/json; charset=UTF-8'})
      headerCF.update({'x-requested-with': 'XMLHttpRequest'})

      payload = '{"firstName":"'+accountDict['first_name']+'" , "lastName":"'+accountDict['last_name']+'", "company":"", "address1":"'+accountDict['address']+'", "address2":"", "city":"'+accountDict['city']+'", "postcode":"'+accountDict['zipcode']+'", "country":"'+accountDict['country_id']+'"}'

      proxy = prx

      print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Setting shipping address..' + utility.bcolors.ENDC)
      logging.info('[WCH] ' + utility.threadTime(mode) + ' Setting shhipping address..')

      while True:

            try:
                  r = s.post('https://www.workingclassheroes.co.uk/wsCitrusStore.asmx/WightLoadShippingOptions',  data = payload, headers=headerCF, proxies = proxy)

                  if str(r.status_code) == '503':
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue
            
            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue

            try:
                  json.loads(r.text)

                  print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully set shipping address!' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '['+str(r.status_code)+'] Successfully set shipping address!')
                  break

            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed setting shipping address, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed setting shipping address, retrying..')
                  time.sleep(delay)
                  continue

      return proxy

def ThirdSet(s, mode, accountDict, prx):
    
      headerCF = dict(s.headers)
      headerCF.update({'referer': 'https://www.workingclassheroes.co.uk/ssl/secure/'})
      headerCF.update({'content-type': 'application/json; charset=UTF-8'})
      headerCF.update({'x-requested-with': 'XMLHttpRequest'})

      date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

      payload = '{"firstName":"'+accountDict['first_name']+'" , "lastName":"'+accountDict['last_name']+'", "company":"", "address1":"'+accountDict['address']+'", "address2":"", "city":"'+accountDict['city']+'", "postcode":"'+accountDict['zipcode']+'", "phone":"'+accountDict['phone_number']+'", "country":"'+accountDict['country_id']+'","selectedShipping":{"IsPremium":false,"bookingCode":"RoyalMail48","carrierCode":"RoyalMail48","carrierCustom1":"","carrierCustom2":"","carrierCustom3":"","carrierServiceCode":"RoyalMail48","carrierServiceTypeCode":"","collectionSlots":null,"collectionWindow":{"to":"'+date+'.7881959+01:00","from":"'+date+'.7881959+01:00"},"cutOffDateTime":"'+date+'.7881959+01:00","deliverySlots":null,"deliveryWindow":{"to":"'+date+'.7881959+01:00","from":"'+date+'.7881959+01:00"},"groupCodes":null,"name":"3 - 5 Working Days Unsigned","nominatableCollectionSlot":false,"nominatableDeliverySlot":false,"recipientTimeZone":null,"score":0,"senderTimeZone":null,"shippingCharge":2.5,"shippingCost":1.89,"taxAndDuty":0,"taxAndDutyStatusText":null,"vatRate":0},"nickname":""}'

      proxy = prx

      print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Setting courier info..' + utility.bcolors.ENDC)
      logging.info('[WCH] ' + utility.threadTime(mode) + ' Setting courier info..')

      while True:

            try:
                  r = s.post('https://www.workingclassheroes.co.uk/wsCitrusStore.asmx/WightPostShippingDetails',  data = payload, headers= headerCF, proxies = proxy)

                  if str(r.status_code) == '503':
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue
            
            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue

            try:
                  firstJSON = json.loads(r.text)

                  if str(firstJSON['d']).split('{\"status\":')[1].split(',\"errorMsg\"')[0]:
                        print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully set courier info [RoyalMail48]' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '['+str(r.status_code)+'] Successfully set courier info [RoyalMail48')
                        break
                  else:
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed setting courier info, retrying..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '[ERROR] ['+str(firstJSON)+'] Failed setting courier info, retrying..')
                        time.sleep(delay)
                        continue

            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed setting courier info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed setting courier info, retrying..')
                  time.sleep(delay)
                  continue
      
      return proxy

def CompleteCC(s, mode, accountDict, prx):
    
      headerCF = dict(s.headers)
      headerCF.update({'referer': 'https://www.workingclassheroes.co.uk/ssl/secure/'})
      headerCF.update({'content-type': 'application/json; charset=UTF-8'})
      headerCF.update({'x-requested-with': 'XMLHttpRequest'})

      date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
      
      payload = '{"MethodType":"Standard","SpecialInstructions":"","PaymentMethod":"credit card","cardTypeUid":9,"cardType":"MasterCard","cardNumber":"'+accountDict['credit_card']+'","secureCode":"'+accountDict['cvv']+'","expMonth":"'+accountDict['month']+'","expYear":"'+accountDict['year']+'","token":"","selectedShipping":{"IsPremium":false,"bookingCode":"","carrierCode":"","carrierCustom1":"","carrierCustom2":"","carrierCustom3":"","carrierServiceCode":"","carrierServiceTypeCode":"","collectionSlots":null,"collectionWindow":{"to":"2019-08-12T00:00:00","from":"2019-08-12T00:00:00"},"cutOffDateTime":"2019-08-12T00:00:00","deliverySlots":null,"deliveryWindow":{"to":"2019-08-13T00:00:00","from":"2019-08-13T00:00:00"},"groupCodes":null,"name":"","nominatableCollectionSlot":false,"nominatableDeliverySlot":false,"recipientTimeZone":null,"score":0,"senderTimeZone":null,"shippingCharge":0,"shippingCost":0,"taxAndDuty":0,"taxAndDutyStatusText":null,"vatRate":0},"paypalToken":"","payPalPayerID":""}'

      proxy = prx

      print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Completing checkout..' + utility.bcolors.ENDC)
      logging.info('[WCH] ' + utility.threadTime(mode) + ' Completing checkout..')

      while True:

            try:
                  r = s.post('https://www.workingclassheroes.co.uk/wsCitrusStore.asmx/WightHandlePaymentSelector',  data = payload, headers=headerCF, proxies = proxy)

                  if str(r.status_code) == '503':
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue
            
            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue

            try:
                  firstJSON = json.loads(r.text)

                  if str(firstJSON['d']).split('{\"status\":')[1].split(',\"errorMsg\"')[0]:
                        print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully checked out' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '['+str(r.status_code)+'] Successfully checked out')
                        setTitle(1)
                        break
                  else:
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed completing checkout, retrying..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '[ERROR] ['+str(firstJSON)+'] Failed completing checkout, retrying..')
                        time.sleep(delay)
                        continue

            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed completing checkout, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed completing checkout, retrying..')
                  time.sleep(delay)
                  continue

def Checkout(s, mode, prx):

      print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)

      headerCF = dict(s.headers)
      headerCF.update({'referer': 'https://www.workingclassheroes.co.uk/shoppingcart.aspx'})
      headerCF.update({'content-type': 'application/json; charset=UTF-8'})
      headerCF.update({'x-requested-with': 'XMLHttpRequest'})

      proxy = prx

      while True:

            try:
                  r = s.post('https://www.workingclassheroes.co.uk/wsCitrusStore.asmx/WightPaypalBtnCallback',  data = '{}', headers=headerCF, proxies = proxy) 
                  

                  if str(r.status_code) == '503':
                        print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue

            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one.. ' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' +utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
                  logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
                  time.sleep(delay)
                  continue     
            
            if 'https://www.paypal.com/cgi-bin/webscr?cmd=' in str(r.text):
                  print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '['+str(r.status_code)+'] Successfully checked out!' + utility.bcolors.ENDC)
                  logging.info('[WCH]' + utility.threadTime(mode) + '['+str(r.status_code)+'] Successfully checked out!')
                  checkoutLink = str(json.loads(r.text)['d']['errorMsg']).replace('\u0026','&')
                  setTitle(1)
                  break
            else:
                 print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
                 logging.info('[WCH] ' + utility.threadTime(mode) + '[ERROR] Failed getting PayPal link, retrying..')
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
            productName, productImage, productID, attributeID, sizeDict, prx = GetProductInfo(s, url, mode, prx)
            atcVariant, sizeID = utility.SelectSize(sizeDict, size, mode, 'WCH', configDict)
            
            if atcVariant != -1 and sizeID != 1:
                  break;
      
      start_time = datetime.now()
      print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Adding to cart size: ['+sizeID+']' + utility.bcolors.ENDC)
      logging.info('[WCH] ' + utility.threadTime(mode) + 'Adding to cart size: ['+sizeID+']')
      prx = AddToCart(s, productID, attributeID, atcVariant, url, mode, prx)

      if 'PP' in mode:
            checkoutLink = Checkout(s, mode, prx)
      else:
            prx = FirstSet(s, mode, accountDict, prx)
            prx = SecondSet(s, mode, accountDict, prx)
            prx = ThirdSet(s, mode, accountDict, prx)
            CompleteCC(s, mode, accountDict, prx)
            checkoutLink = 'https://www.workingclassheroes.co.uk/ssl/controls/3DAuthentication/3DRedirect.aspx'

      final_time = utility.getFinalTime(start_time)

      try:
            checkoutLink = utility.getCheckoutLink(s, 'https://www.workingclassheroes.co.uk/', checkoutLink)
      except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
            logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] Failed getting checkout link with cookie!')
            time.sleep(1000)

      
      crissWebhook.sendWCHWebhook(url, productName, sizeID, checkoutLink, productImage, str(final_time), mode)
      crissWebhook.publicWCHWebhook(url, productName, sizeID, productImage, str(final_time), mode)
      crissWebhook.staffWCHWebhook(url, productName, sizeID, productImage, str(final_time), mode)
      
      input('')
      time.sleep(100)

def shockdrop(URL, val, mode):

      title = utility.getTitleHeader() + "  -  WorkingClassHeores  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
      utility.setTitle(title)

      accountDict = {}

      try:
            global allProxies 
            allProxies = utility.loadProxies('wch')
            with open('wch/task.csv', 'r') as csv_file:
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
                                          t = Thread(target=main, args=(line['URL'], 'RANDOM', mode, accountDict))
                                          t.start()

                                    break

                              except Exception as e:
                                    print(utility.threadTime(mode) + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                                    logging.info('[WCH] ' + utility.threadTime(mode) + '[' + str(e) + '] Failed loading task, please check csv file!')
                                    input('Press ENTER to exit.')
                                    sys.exit()
                        else:
                              try:
                                    for tasks in range(0, val):
                                          t = Thread(target=main, args=(line['URL'], 'RANDOM', mode, ""))
                                          t.start()
                                    
                                    break
                              
                              except Exception as e:
                                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                                    logging.info('[WCH] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                                    input('Press ENTER to exit.')
                                    sys.exit()
      except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
            logging.info('[WCH] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
            input('Press ENTER to exit.')
            sys.exit()

def start_main():

      title = utility.getTitleHeader() + "  -  WorkingClassHeores  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
      utility.setTitle(title)


      try:
            global allProxies 
            allProxies = utility.loadProxies('wch')
            with open('wch/task.csv', 'r') as csv_file:
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
                                    logging.info('[WCH] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                                    input('Press ENTER to exit.')
                                    sys.exit()
                        else:
                              try:
                                    t = Thread(target=main, args=(line['URL'], line['SIZE'], line['PAYMENT'], ""))
                                    t.start()
                              except Exception as e:
                                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                                    logging.info('[WCH] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                                    input('Press ENTER to exit.')
                                    sys.exit()
      except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
            logging.info('[WCH] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
            input('Press ENTER to exit.')
            sys.exit()

if __name__ == '__main__':
      start_main()