# -*- coding: utf-8 -*-
#!/bin/env python

''' 7HILLS '''

import requests, signal, json, random, csv, time, sys, re, os, utility, crissWebhook
from bs4 import BeautifulSoup
from datetime import datetime, date
import logging
from threading import Thread, Lock
from os import system

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[7HILLS] ' + utility.threadTime('') + str(exc_value))
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
    

    title = utility.getTitleHeader() + "  -  7Hills  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()

def ProductScraper(session, url, size, prx):

    sizeDict = {}
    super_attr = ''
    proxy = prx

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
    logging.info('[7HILLS] ' + utility.threadTime('') + 'Getting product info..')

    while True:

        try:
            r = session.get(url, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        

        try:
            ''' TITOLO E IMMAGINE '''
            title = soup.find('a', {'class':'highslide main-image'})['title']
            img = soup.find('a', {'class':'highslide main-image'})['href']

        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [TITLE/IMG] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [TITLE/IMG] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

        try:
            ''' CHECKOUT TOKEN '''
            atc = soup.find('form', {'id':'product_addtocart_form'})['action'].replace('http','https')
            form_key = atc.split('/form_key/')[1].split('/')[0]
            product = atc.split('/product/')[1].split('/form_key/')[0]
            
            if 'ONESIZE' not in size:
                super_attr = soup.find('select', {'class':'required-entry super-attribute-select'})['name']
            else:
                break

        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [CHECKOUT TOKEN] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [CHECKOUT TOKEN] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

        try:
            size = str(soup.select('#product-options-wrapper > script:nth-child(2)')[0]).split('(')[1].split(')')[0]
            sizeJSON = json.loads(size)

            for id in sizeJSON['attributes'][str(super_attr).split('[')[1].split(']')[0]]['options']:
                pid = id['id']
                size = id['label']
                sizeDict.update({pid:size})

            if len(sizeDict) == 0:
                print(utility.threadTime('') + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                logging.info('[7HILLS] ' + utility.threadTime('') + 'Product out of stock, retrying..')
                time.sleep(delay)
                continue      
            else:    
                break

        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [SIZES] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [SIZES] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
    
    return title, img, atc, form_key, product, super_attr, sizeDict, proxy

def AddToCart(session, atc, product, form_key, size, super_attr, prx):

    atc_payload = {
        'handles[]': 'default',
        'handles[]': 'STORE_it',
        'handles[]': 'THEME_frontend_argento_argento',
        'handles[]': 'catalog_product_view',
        'handles[]': 'PRODUCT_TYPE_configurable',
        'handles[]': 'PRODUCT_'+product,
        'handles[]': 'customer_logged_out',
        'ajaxpro': '1',
        'in_cart': '1',
        'form_key': form_key,
        'product': product,
        'related_product': '',
        'qty': '1',
        'return_url': ''
    }

    headersXML = {
        'Connection': 'keep-alive',
        'Host': 'www.7hillsroma.com',
        'Origin': 'https://www.7hillsroma.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36', 
        'X-Prototype-Version': '1.7',
        'X-Requested-With': 'XMLHttpRequest'
    }

    if 'ONESIZE' not in size:
        atc_payload.update({super_attr:size})

    proxy = prx

    while True:

        try:

            r = session.post(atc, headers=headersXML, data=atc_payload, allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

        try:
            if json.loads(r.text)['status']:
                print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
                logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully added to cart!')
                setTitle(0)
                break
            else:
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[7HILLS] ' + utility.threadTime('') + '[ERROR] Failed adding to cart, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

    return proxy
  
def Checkout(session, prx):

    print(utility.threadTime('') + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[7HILLS] ' + utility.threadTime('') + 'Checking out..')

    proxy = prx

    while True:

        try:
            r = session.get('https://www.7hillsroma.com/it/paypal/express/start/button/1/', allow_redirects=True, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed checking out, retrying..')
            time.sleep(delay)
            continue

        if 'token' in r.url:
            print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully checked out!')
            setTitle(1)
            break
        else:
            print(utility.threadTime('') + utility.bcolors.FAIL + '[' + str(r.status_code) + '] Failed getting PayPal link, retrying..' + utility.bcolors.ENDC)
            logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Failed getting PayPal link, retrying..')
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

def main(url, size):

    prx = GetNewProxy()
    s = requests.session()

    if 'ONESIZE' not in size:
        while True:
            title, img, atc, form_key, product, super_attr, sizeList, prx = ProductScraper(s, url, size, prx)
            pid, sizeID = utility.SelectSize(sizeList, size, '', '7HILLS', configDict)

            if pid != -1 and sizeID != 1:
                break;
    else:
        title, img, atc, form_key, product, super_attr, sizeList, prx = ProductScraper(s, url, size, prx)
        pid = 'ONESIZE'
        sizeID = 'ONESIZE'
    
    start_time = datetime.now()
    print(utility.threadTime('') + utility.bcolors.WARNING + 'Adding to cart size: [' + sizeID + ']' + utility.bcolors.ENDC)
    logging.info('[7HILLS] ' + utility.threadTime('') + 'Adding to cart size: [' + sizeID + ']')
    
    prx = AddToCart(s, atc, product, form_key, pid, super_attr, prx)
    link = Checkout(s, prx)
    final_time = datetime.now()-start_time

    try:
        link = utility.getCheckoutLink(s, 'https://www.7hillsroma.com/', link)
    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
        logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(e) + '] Failed getting checkout link with cookie!')
        time.sleep(1000)    

    crissWebhook.sendWebhook('7Hills', url, '', title, sizeID, link, img, 'PayPal', final_time)
    crissWebhook.publicWebhook('7Hills', url, title, sizeID, img, final_time, 'PayPal')
    crissWebhook.staffWebhook('7Hills', title, sizeID, img, str(final_time))

    input('')
    time.sleep(100)

def shockdrop(URL, val):

    title = utility.getTitleHeader() + "  -  7Hills  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    global allProxies 
    allProxies = utility.loadProxies('hills')

    for tasks in range(0, val):
        t = Thread(target=main, args=(URL, 'RANDOM'))
        t.start()

def start_main():

    title = utility.getTitleHeader() + "  -  7Hills  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies 
        allProxies = utility.loadProxies('hills')
        with open('hills/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:
                t = Thread(target=main, args=(line['URL'], line['SIZE']))
                t.start()
    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[7HILLS] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)

if __name__ == '__main__':
    start_main() 