# -*- coding: utf-8 -*-
#!/bin/env python

import requests, signal, json, random, csv, time, sys, re, crissWebhook, os, utility, cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime
import logging
from os import system
from threading import Thread, Lock

''' HOLYPOP '''

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[HOLYPOP] ' + utility.threadTime('') + str(exc_value))
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
    

    title = utility.getTitleHeader() + "  -  Holypop  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)
    mutex.release()

def Login(session, email, password, mode, prx):

    login_payload = {
        'controller': 'auth',
        'action': 'authenticate',
        'type': 'standard',
        'extension': 'holypop',
        'credential': email,
        'password': password,
        'language': 'EN',
        'version': 348,
        'cookieVersion': 310
    }

    proxy = prx

    headerCF = dict(session.headers)
    headerCF.update({'x-requested-with': 'XMLHttpRequest'})

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Logging in with: ' + email + utility.bcolors.ENDC)
    logging.info('[HOLYPOP] ' + utility.threadTime(mode) + 'Logging in with: ' + email)


    while True:

        try:

            r = session.post('https://www.holypopstore.com/index.php', headers=headerCF, allow_redirects=True, data=login_payload, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed loggin in, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed loggin in, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed loggin in, retrying..')
            time.sleep(delay)
            continue

        try:
            loginJson = json.loads(r.text)

            if loginJson['success']:
                print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully logged in!' + utility.bcolors.ENDC)
                logging.info('[HOLYPOP] ' + utility.threadTime(mode) +  '[' + str(r.status_code) + '] Successfully logged in!')
                break
            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[' + str(loginJson['error']['message']) + '] Failed loggin in, retrying..' + utility.bcolors.ENDC)
                logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(loginJson['error']['message']) + '] [ERROR] Failed loggin in, retrying..')
                time.sleep(delay)
                continue

        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed loggin in, probably blacklisted, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed loggin in, probably blacklisted, retrying..')
            time.sleep(delay)
            continue

    return proxy

def ScrapeSizeInfo(session, productUrl, mode, prx):

    sizeDict = {}
    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
    logging.info('[HOLYPOP] ' + utility.threadTime(mode) + 'Getting product info..')

    while True:
        
        try:
            r = session.get(productUrl, proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue

        try:
            soup = BeautifulSoup(r.text.encode('utf-8'), "html.parser")
            ListOfRawSizes = soup.find_all('script')

            for line in ListOfRawSizes:
                if 'preloadedStock' in str(line):

                    stockJson = json.loads(str(line).split('var preloadedStock = ')[1].split('];')[0] + ']')
                    #print(stockJson)
                    
                    for elem in stockJson:
                        pid_size = elem['stockItemId']
                        #print(pid_size)
                        size = elem['variant']
                        #print(size)
                        if elem['isInStock']:
                            sizeDict.update({pid_size:size})

                    break
                        
            if len(sizeDict) == 0:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                logging.info('[HOLYPOP] ' + utility.threadTime(mode) + 'Product out of stock, retrying..')
                time.sleep(delay)
                continue
            else:
                break

        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
            time.sleep(delay)
            continue
    
    return sizeDict, proxy

def AddToCart(session, variant, mode, prx):

    atc_payload = {
        'controller': 'orders',
        'action': 'addStockItemToBasket',
        'stockItemId': variant,
        'quantity': 1,
        'extension': 'holypop',
        'version': 348,
        'cookieVersion': 310
    }

    proxy = prx

    headerCF = dict(session.headers)
    headerCF.update({'x-requested-with': 'XMLHttpRequest'})

    while True:
        try:
            r = session.post('https://www.holypopstore.com/index.php', headers=headerCF, data=atc_payload, proxies=proxy)

            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

        try:
            addToCartJson = json.loads(r.text)

            if addToCartJson['success']:
                print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
                logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Successfully added to cart!')

                productName = addToCartJson['payload'][0]['imageObject']['altTitle']
                productImg = str(addToCartJson['payload'][0]['imageObject']['thumbUrl']).replace('\/','/')
                sizeValue = addToCartJson['payload'][0]['attributes'][0]['value']['value']
                productUrl = str(addToCartJson['payload'][0]['permalink']).replace('\/','/')
                setTitle(0)
                break
            else:
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[' + addToCartJson['error']['message'] + '] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + addToCartJson['error']['message'] + '] [ERROR] Failed adding to cart, retrying..')
                time.sleep(delay)
                continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
            time.sleep(delay)
            continue

    return productName, productImg, sizeValue, productUrl, proxy

def Checkout(session, mode, prx):

    proxy = prx

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Checking out..' + utility.bcolors.ENDC)
    logging.info('[HOLYPOP] ' + utility.threadTime(mode) + 'Checking out..')

    while True:
    
        try:
            r = session.get('https://www.holypopstore.com/en/orders/review', proxies=proxy)
        
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue
        
        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue

        try:
            shippingAddressId = BeautifulSoup(r.text, 'html.parser').find('option', {'selected':'selected'})['value']
            break
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [ADDRESS ID] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] [ADDRESS ID] Failed checking out, retrying..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue

    checkout_payload = {
        'secretly': 'false',
        'hardErrorize': 'false',
        'billingAddressId': shippingAddressId,
        'shippingAddressId': shippingAddressId,
        'shipmentFlow': 'DELIVERY',
        'newAddresses': 0,
        'requestInvoice': 0,
        'notes': '', 
        'paymentMethodId': 1,
        'paymentMethodAccountId': 1,
        'shipments[0][shipmentFlow]': 'DELIVERY',
        'shipments[0][addressId]': shippingAddressId,
        'shipments[0][shipperId]': 10,
        'shipments[0][shipperAccountId]': 4,
        'toDisplay': 0,
        'extension': 'holypop',
        'controller': 'orders',
        'action': 'save',
        'language': 'EN',
        'version': 348,
        'cookieVersion': 310
    }

    headerCF = dict(session.headers)
    headerCF.update({'x-requested-with': 'XMLHttpRequest'})

    while True:

        try:
            r = session.post('https://www.holypopstore.com/index.php', headers=headerCF, data=checkout_payload, proxies=proxy)
            
            if str(r.status_code) == '503':
                print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                proxy = GetNewProxy()
                time.sleep(delay)
                continue

        except requests.exceptions.ProxyError as errp:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.ConnectionError as errh:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
            proxy = GetNewProxy()
            time.sleep(delay)
            continue
        except requests.exceptions.Timeout as errt:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[TIMEOUT] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(errt) + '] [TIMEOUT] Failed checking out, retrying..')
            time.sleep(delay)
            continue
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] Failed checking out, retrgying..')
            time.sleep(delay)
            continue

        try:
            paymentJson = json.loads(r.text)
            orderId = paymentJson['payload']['orderId']

            print(utility.threadTime(mode) + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!'  + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(r.status_code) + '] Successfully checked out!')
            
            break
        except Exception as e:
            print(utility.threadTime(mode) + utility.bcolors.FAIL + '[ERROR] [OOS] Failed checking out, retrying..' + utility.bcolors.ENDC)
            logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(e) + '] [ERROR] [OOS] Failed checking out, retrying..')
            time.sleep(delay)
            continue

    return orderId, proxy

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

def main(pid, username, password, size, mode):

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

    prx = Login(s, username, password, mode, prx)

    if('URL' in mode):
        while True:
            sizeDict, prx = ScrapeSizeInfo(s, pid, mode, prx)
            variant, sizeID = utility.SelectSize(sizeDict, size, mode, 'HOLYPOP', configDict)

            if variant != -1 and sizeID != 1:
                break;
    else:
        variant = pid
        sizeID = pid
    
    start_time = datetime.now()

    print(utility.threadTime(mode) + utility.bcolors.WARNING + 'Adding to cart size: [' + sizeID + ']' + utility.bcolors.ENDC)
    logging.info('[HOLYPOP] ' + utility.threadTime(mode) + 'Adding to cart size: [' + sizeID + ']')
    productTitle, productImage, sizeID, url, prx = AddToCart(s, variant, mode, prx)

    orderId, prx = Checkout(s, mode, prx)
    checkoutLink = 'https://www.holypopstore.com/it/orders/checkout/' + str(orderId) + '?paymentMethodId=1&paymentMethodAccountId=1'

    final_time = datetime.now()-start_time

    #L'IMMAGINE E' BUONA MA NON LA METTE QUINDI FACCIAMO COSI'
    productImage = 'https://i.imgur.com/ZLsoszA.png'

    try:
        checkout_link = utility.getCheckoutLink(s, 'https://www.holypopstore.com/', checkoutLink)
    except Exception as e:
        print(utility.threadTime(mode) + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
        logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(e) + ']Failed getting checkout link with cookie!')
        time.sleep(100)

    crissWebhook.sendHolypopWebhook('Successfully checked out!', url, productTitle, sizeID, checkout_link, productImage, str(final_time), username, 0xff00dd, mode, password)
    crissWebhook.publicHolypopWebhook('Successfully checked out!', url, productTitle, sizeID, productImage, mode, 'PayPal', str(final_time))
    crissWebhook.staffWebhook('Holypop', productTitle, sizeID, productImage, final_time)

    time.sleep(100)
    input('')

def shockdrop(URL, val):

    title = utility.getTitleHeader() + "  -  Holypop  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    accountDict = {}

    if 'www' in URL:
        mode = 'Direct URL'
    else:
        mode = 'PID'

    try:
        global allProxies
        allProxies = utility.loadProxies('holypop')
        with open('holypop/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:
                try:
                    for tasks in range(0, val):
                        t = Thread(target=main, args=(URL, line['USERNAME'], line['PASSWORD'], 'RANDOM', mode))
                        t.start()
                    
                    break

                except Exception as e:
                    print(utility.threadTime(mode) + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                    logging.info('[HOLYPOP] ' + utility.threadTime(mode) + '[' + str(e) + '] Failed loading task, please check csv file!')
                    input('Press ENTER to exit.')
                    sys.exit(-1)

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[HOLYPOP] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)

def start_main():

    title = utility.getTitleHeader() + "  -  Holypop  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
    utility.setTitle(title)

    try:
        global allProxies
        allProxies = utility.loadProxies('holypop')
        with open('holypop/task.csv', 'r') as csv_file:
            csv_key = csv.DictReader(csv_file)

            for line in csv_key:
                try:

                    if 'www' in line['PRODUCT']:
                        mode = 'Direct URL'
                    else:
                        mode = 'PID'

                    t = Thread(target=main, args=(line['PRODUCT'], line['USERNAME'], line['PASSWORD'], line['SIZE'], mode))
                    t.start()
                except Exception as e:
                    print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                    logging.info('[HOLYPOP] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                    input('Press ENTER to exit.')
                    sys.exit(-1)

    except Exception as e:
        print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
        logging.info('[HOLYPOP] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
        input('Press ENTER to exit.')
        sys.exit(-1)

if __name__ == '__main__':
    start_main()