import requests, time, signal, sys, json, re, csv, random, os, crissWebhook, cloudscraper, utility
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from os import system
from threading import Thread, Lock

''' SOTF '''

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    logging.info('[SOTF] ' + utility.threadTime('') + str(exc_value))
    input("Press ENTER to exit")
    sys.exit(-1)

sys.excepthook = show_exception_and_exit

os.chdir(os.path.dirname(sys.executable))
configDict = utility.getDictConfig()
delay = float(configDict.get('delay'))
api_key = configDict.get('2captcha')
allProxies = None

sumup_payload = {
      'nazione_opt': '85',
      'nazione[85]': 'IT',
      'province[AG]': '84',
      'province[AL]': '6',
      'province[AN]': '42',
      'province[AO]': '7',
      'province[AR]': '51',
      'province[AP]': '44',
      'province[AT]': '5',
      'province[AV]': '64',
      'province[BA]': '72',
      'province[BL]': '25',
      'province[BN]': '62',
      'province[BG]': '16',
      'province[BI]': '96',
      'province[BO]': '37',
      'province[BZ]': '21',
      'province[BS]': '17',
      'province[BR]': '74',
      'province[CA]': '92',
      'province[CL]': '85',
      'province[CB]': '70',
      'province[CI]': '124',
      'province[CE]': '61',
      'province[CT]': '87',
      'province[CZ]': '79',
      'province[CH]': '69',
      'province[VO]': '105',
      'province[CO]': '13',
      'province[CS]': '78',
      'province[CR]': '19',
      'province[KR]': '101',
      'province[CN]': '4',
      'province[EN]': '86',
      'province[EE]': '106',
      'province[FM]': '181',
      'province[FE]': '38',
      'province[FI]': '48',
      'province[FG]': '71',
      'province[FC]': '40',
      'province[FR]': '60',
      'province[GE]': '10',
      'province[GO]': '31',
      'province[GR]': '53',
      'province[IM]': '8',
      'province[IS]': '94',
      'province[AQ]': '66',
      'province[SP]': '11',
      'province[LT]': '59',
      'province[LE]': '75',
      'province[LC]': '97',
      'province[LI]': '49',
      'province[LO]': '98',
      'province[LU]': '46',
      'province[MC]': '43',
      'province[MN]': '20',
      'province[MS]': '45',
      'province[MT]': '77',
      'province[MD]': '123',
      'province[ME]': '83',
      'province[MI]': '15',
      'province[MO]': '36',
      'province[MB]': '182',
      'province[NA]': '63',
      'province[NO]': '3',
      'province[NU]': '91',
      'province[OG]': '122',
      'province[OT]': '121',
      'province[OR]': '95',
      'province[PD]': '28',
      'province[PA]': '82',
      'province[PR]': '34',
      'province[PV]': '18',
      'province[PG]': '54',
      'province[PU]': '41',
      'province[PE]': '68',
      'province[PC]': '33',
      'province[PI]': '50',
      'province[PT]': '47',
      'province[PN]': '93',
      'province[PZ]': '76',
      'province[PO]': '100',
      'province[RG]': '88',
      'province[RA]': '39',
      'province[RC]': '80',
      'province[RE]': '35',
      'province[SM]': '104',
      'province[RI]': '57',
      'province[RN]': '99',
      'province[RM]': '58',
      'province[RO]': '29',
      'province[SA]': '65',
      'province[SS]': '90',
      'province[SV]': '9',
      'province[SI]': '52',
      'province[SR]': '89',
      'province[SO]': '14',
      'province[SU]': '183',
      'province[TA]': '73',
      'province[TE]': '67',
      'province[TR]': '55',
      'province[TO]': '1',
      'province[TP]': '81',
      'province[TN]': '22',
      'province[TV]': '26',
      'province[TS]': '32',
      'province[UD]': '30',
      'province[VA]': '12',
      'province[VE]': '27',
      'province[VB]': '103',
      'province[VC]': '2',
      'province[VR]': '23',
      'province[VV]': '102',
      'province[VI]': '24',
      'province[VT]': '56',
      'Clienti_indirizzo': '',
      'Clienti_numcivico': '',
      'Clienti_cap': '',
      'Clienti_citta': '',
      'province_ID': '',
      'country': 'IT',
      'Clienti_tel': '',
      'sped_to_cli': '1',
      'trigger_sped_to_cli': '1',
      'Clienti_sedi_ID': '',
      'nazione_sedi[211]': 'AE',
      'nazione_sedi[1]': 'AF',
      'nazione_sedi[2]': 'AL',
      'nazione_sedi[3]': 'DZ',
      'nazione_sedi[4]': 'AD',
      'nazione_sedi[5]': 'AO',
      'nazione_sedi[6]': 'AG',
      'nazione_sedi[7]': 'SA',
      'nazione_sedi[8]': 'AR',
      'nazione_sedi[9]': 'AM',
      'nazione_sedi[10]': 'AU',
      'nazione_sedi[11]': 'AT',
      'nazione_sedi[12]': 'AZ',
      'nazione_sedi[13]': 'BS',
      'nazione_sedi[202]': 'BH',
      'nazione_sedi[14]': 'BH',
      'nazione_sedi[15]': 'BD',
      'nazione_sedi[16]': 'BB',
      'nazione_sedi[17]': 'BE',
      'nazione_sedi[18]': 'BZ',
      'nazione_sedi[19]': 'BJ',
      'nazione_sedi[20]': 'BT',
      'nazione_sedi[21]': 'BY',
      'nazione_sedi[22]': 'BO',
      'nazione_sedi[23]': 'BA',
      'nazione_sedi[24]': 'BW',
      'nazione_sedi[25]': 'BR',
      'nazione_sedi[26]': 'BN',
      'nazione_sedi[27]': 'BG',
      'nazione_sedi[28]': 'BF',
      'nazione_sedi[29]': 'BI',
      'nazione_sedi[30]': 'KH',
      'nazione_sedi[31]': 'CM',
      'nazione_sedi[32]': 'CA',
      'nazione_sedi[33]': 'CV',
      'nazione_sedi[34]': 'TD',
      'nazione_sedi[35]': 'CL',
      'nazione_sedi[36]': 'CN',
      'nazione_sedi[37]': 'CY',
      'nazione_sedi[38]': 'CO',
      'nazione_sedi[39]': 'KM',
      'nazione_sedi[40]': 'CG',
      'nazione_sedi[41]': 'KP',
      'nazione_sedi[43]': 'CI',
      'nazione_sedi[44]': 'CR',
      'nazione_sedi[45]': 'HR',
      'nazione_sedi[47]': 'DK',
      'nazione_sedi[48]': 'DM',
      'nazione_sedi[210]': 'AE',
      'nazione_sedi[207]': 'EC',
      'nazione_sedi[49]': 'EC',
      'nazione_sedi[208]': 'EG',
      'nazione_sedi[50]': 'EG',
      'nazione_sedi[51]': 'SV',
      'nazione_sedi[52]': 'AE',
      'nazione_sedi[53]': 'ER',
      'nazione_sedi[54]': 'EE',
      'nazione_sedi[55]': 'ET',
      'nazione_sedi[204]': 'PH',
      'nazione_sedi[56]': 'PH',
      'nazione_sedi[57]': 'FI',
      'nazione_sedi[58]': 'FR',
      'nazione_sedi[59]': 'GA',
      'nazione_sedi[60]': 'GM',
      'nazione_sedi[61]': 'GE',
      'nazione_sedi[62]': 'DE',
      'nazione_sedi[63]': 'GH',
      'nazione_sedi[64]': 'JM',
      'nazione_sedi[206]': 'JP',
      'nazione_sedi[65]': 'JP',
      'nazione_sedi[197]': 'GI',
      'nazione_sedi[66]': 'DJ',
      'nazione_sedi[67]': 'JO',
      'nazione_sedi[68]': 'GR',
      'nazione_sedi[69]': 'GD',
      'nazione_sedi[201]': 'GL',
      'nazione_sedi[70]': 'GT',
      'nazione_sedi[195]': 'GGY',
      'nazione_sedi[71]': 'GN',
      'nazione_sedi[72]': 'GQ',
      'nazione_sedi[73]': 'GW',
      'nazione_sedi[74]': 'GY',
      'nazione_sedi[75]': 'HT',
      'nazione_sedi[76]': 'HN',
      'nazione_sedi[215]': 'HK',
      'nazione_sedi[209]': 'IN',
      'nazione_sedi[77]': 'IN',
      'nazione_sedi[205]': 'ID',
      'nazione_sedi[78]': 'ID',
      'nazione_sedi[79]': 'IR',
      'nazione_sedi[80]': 'IQ',
      'nazione_sedi[81]': 'IE',
      'nazione_sedi[82]': 'IS',
      'nazione_sedi[194]': 'IM',
      'nazione_sedi[198]': 'IB',
      'nazione_sedi[199]': 'ES-',
      'nazione_sedi[200]': 'FO',
      'nazione_sedi[83]': 'FJ',
      'nazione_sedi[84]': 'IL',
      'nazione_sedi[85]': 'IT',
      'nazione_sedi[196]': 'JEY',
      'nazione_sedi[87]': 'KZ',
      'nazione_sedi[88]': 'KE',
      'nazione_sedi[89]': 'KG',
      'nazione_sedi[90]': 'KI',
      'nazione_sedi[91]': 'KW',
      'nazione_sedi[92]': 'LA',
      'nazione_sedi[93]': 'LS',
      'nazione_sedi[94]': 'LV',
      'nazione_sedi[95]': 'LB',
      'nazione_sedi[96]': 'LR',
      'nazione_sedi[97]': 'LY',
      'nazione_sedi[98]': 'LI',
      'nazione_sedi[99]': 'LT',
      'nazione_sedi[100]': 'LU',
      'nazione_sedi[101]': 'MK',
      'nazione_sedi[102]': 'MG',
      'nazione_sedi[103]': 'MW',
      'nazione_sedi[203]': 'MY',
      'nazione_sedi[104]': 'MY',
      'nazione_sedi[105]': 'MV',
      'nazione_sedi[106]': 'ML',
      'nazione_sedi[107]': 'MT',
      'nazione_sedi[108]': 'MA',
      'nazione_sedi[109]': 'MH',
      'nazione_sedi[110]': 'MR',
      'nazione_sedi[111]': 'MU',
      'nazione_sedi[112]': 'MX',
      'nazione_sedi[113]': 'FM',
      'nazione_sedi[114]': 'MD',
      'nazione_sedi[115]': 'MC',
      'nazione_sedi[116]': 'MN',
      'nazione_sedi[117]': 'MZ',
      'nazione_sedi[118]': 'MM',
      'nazione_sedi[119]': 'NA',
      'nazione_sedi[120]': 'NR',
      'nazione_sedi[121]': 'NP',
      'nazione_sedi[122]': 'NI',
      'nazione_sedi[123]': 'NE',
      'nazione_sedi[124]': 'NG',
      'nazione_sedi[125]': 'NO',
      'nazione_sedi[126]': 'NZ',
      'nazione_sedi[127]': 'OM',
      'nazione_sedi[128]': 'NL',
      'nazione_sedi[129]': 'PK',
      'nazione_sedi[130]': 'PW',
      'nazione_sedi[131]': 'PA',
      'nazione_sedi[132]': 'PG',
      'nazione_sedi[133]': 'PY',
      'nazione_sedi[134]': 'PE',
      'nazione_sedi[135]': 'PL',
      'nazione_sedi[136]': 'PT',
      'nazione_sedi[137]': 'QA',
      'nazione_sedi[138]': 'GB',
      'nazione_sedi[139]': 'CZ',
      'nazione_sedi[140]': 'CF',
      'nazione_sedi[142]': 'DO',
      'nazione_sedi[143]': 'RO',
      'nazione_sedi[144]': 'RW',
      'nazione_sedi[216]': 'RU',
      'nazione_sedi[146]': 'KN',
      'nazione_sedi[147]': 'LC',
      'nazione_sedi[148]': 'VC',
      'nazione_sedi[150]': 'WS',
      'nazione_sedi[151]': 'SM',
      'nazione_sedi[152]': 'VA',
      'nazione_sedi[153]': 'ST',
      'nazione_sedi[154]': 'SC',
      'nazione_sedi[155]': 'SN',
      'nazione_sedi[156]': 'SL',
      'nazione_sedi[157]': 'SG',
      'nazione_sedi[158]': 'SY',
      'nazione_sedi[159]': 'SK',
      'nazione_sedi[160]': 'SI',
      'nazione_sedi[161]': 'SO',
      'nazione_sedi[162]': 'ES',
      'nazione_sedi[163]': 'LK',
      'nazione_sedi[164]': 'US',
      'nazione_sedi[165]': 'ZA',
      'nazione_sedi[212]': 'KR',
      'nazione_sedi[42]': 'KR',
      'nazione_sedi[166]': 'SD',
      'nazione_sedi[167]': 'SR',
      'nazione_sedi[168]': 'SE',
      'nazione_sedi[169]': 'CH',
      'nazione_sedi[170]': 'SZ',
      'nazione_sedi[171]': 'TJ',
      'nazione_sedi[172]': 'TW',
      'nazione_sedi[173]': 'TZ',
      'nazione_sedi[213]': 'TH',
      'nazione_sedi[174]': 'TH',
      'nazione_sedi[175]': 'TL',
      'nazione_sedi[176]': 'TG',
      'nazione_sedi[177]': 'TO',
      'nazione_sedi[178]': 'TT',
      'nazione_sedi[179]': 'TN',
      'nazione_sedi[214]': 'TR',
      'nazione_sedi[180]': 'TR',
      'nazione_sedi[181]': 'TM',
      'nazione_sedi[182]': 'TV',
      'nazione_sedi[183]': 'UA',
      'nazione_sedi[184]': 'UG',
      'nazione_sedi[185]': 'HU',
      'nazione_sedi[186]': 'UY',
      'nazione_sedi[187]': 'UZ',
      'nazione_sedi[188]': 'VU',
      'nazione_sedi[189]': 'VE',
      'nazione_sedi[190]': 'VN',
      'nazione_sedi[191]': 'YE',
      'nazione_sedi[192]': 'ZM',
      'nazione_sedi[193]': 'ZW',
      'Clienti_sedi_Nazioni_ID': '85',
      'province_sedi[AG]': '84',
      'province_sedi[AL]': '6',
      'province_sedi[AN]': '42',
      'province_sedi[AO]': '7',
      'province_sedi[AR]': '51',
      'province_sedi[AP]': '44',
      'province_sedi[AT]': '5',
      'province_sedi[AV]': '64',
      'province_sedi[BA]': '72',
      'province_sedi[BL]': '25',
      'province_sedi[BN]': '62',
      'province_sedi[BG]': '16',
      'province_sedi[BI]': '96',
      'province_sedi[BO]': '37',
      'province_sedi[BZ]': '21',
      'province_sedi[BS]': '17',
      'province_sedi[BR]': '74',
      'province_sedi[CA]': '92',
      'province_sedi[CL]': '85',
      'province_sedi[CB]': '70',
      'province_sedi[CI]': '124',
      'province_sedi[CE]': '61',
      'province_sedi[CT]': '87',
      'province_sedi[CZ]': '79',
      'province_sedi[CH]': '69',
      'province_sedi[VO]': '105',
      'province_sedi[CO]': '13',
      'province_sedi[CS]': '78',
      'province_sedi[CR]': '19',
      'province_sedi[KR]': '101',
      'province_sedi[CN]': '4',
      'province_sedi[EN]': '86',
      'province_sedi[EE]': '106',
      'province_sedi[FM]': '181',
      'province_sedi[FE]': '38',
      'province_sedi[FI]': '48',
      'province_sedi[FG]': '71',
      'province_sedi[FC]': '40',
      'province_sedi[FR]': '60',
      'province_sedi[GE]': '10',
      'province_sedi[GO]': '31',
      'province_sedi[GR]': '53',
      'province_sedi[IM]': '8',
      'province_sedi[IS]': '94',
      'province_sedi[AQ]': '66',
      'province_sedi[SP]': '11',
      'province_sedi[LT]': '59',
      'province_sedi[LE]': '75',
      'province_sedi[LC]': '97',
      'province_sedi[LI]': '49',
      'province_sedi[LO]': '98',
      'province_sedi[LU]': '46',
      'province_sedi[MC]': '43',
      'province_sedi[MN]': '20',
      'province_sedi[MS]': '45',
      'province_sedi[MT]': '77',
      'province_sedi[MD]': '123',
      'province_sedi[ME]': '83',
      'province_sedi[MI]': '15',
      'province_sedi[MO]': '36',
      'province_sedi[MB]': '182',
      'province_sedi[NA]': '63',
      'province_sedi[NO]': '3',
      'province_sedi[NU]': '91',
      'province_sedi[OG]': '122',
      'province_sedi[OT]': '121',
      'province_sedi[OR]': '95',
      'province_sedi[PD]': '28',
      'province_sedi[PA]': '82',
      'province_sedi[PR]': '34',
      'province_sedi[PV]': '18',
      'province_sedi[PG]': '54',
      'province_sedi[PU]': '41',
      'province_sedi[PE]': '68',
      'province_sedi[PC]': '33',
      'province_sedi[PI]': '50',
      'province_sedi[PT]': '47',
      'province_sedi[PN]': '93',
      'province_sedi[PZ]': '76',
      'province_sedi[PO]': '100',
      'province_sedi[RG]': '88',
      'province_sedi[RA]': '39',
      'province_sedi[RC]': '80',
      'province_sedi[RE]': '35',
      'province_sedi[SM]': '104',
      'province_sedi[RI]': '57',
      'province_sedi[RN]': '99',
      'province_sedi[RM]': '58',
      'province_sedi[RO]': '29',
      'province_sedi[SA]': '65',
      'province_sedi[SS]': '90',
      'province_sedi[SV]': '9',
      'province_sedi[SI]': '52',
      'province_sedi[SR]': '89',
      'province_sedi[SO]': '14',
      'province_sedi[SU]': '183',
      'province_sedi[TA]': '73',
      'province_sedi[TE]': '67',
      'province_sedi[TR]': '55',
      'province_sedi[TO]': '1',
      'province_sedi[TP]': '81',
      'province_sedi[TN]': '22',
      'province_sedi[TV]': '26',
      'province_sedi[TS]': '32',
      'province_sedi[UD]': '30',
      'province_sedi[VA]': '12',
      'province_sedi[VE]': '27',
      'province_sedi[VB]': '103',
      'province_sedi[VC]': '2',
      'province_sedi[VR]': '23',
      'province_sedi[VV]': '102',
      'province_sedi[VI]': '24',
      'province_sedi[VT]': '56',
      'Clienti_sedi_nome': '',
      'Clienti_sedi_cognome': '',
      'Clienti_sedi_indirizzo': '',
      'Clienti_sedi_numcivico': '',
      'Clienti_sedi_cap': '',
      'Clienti_sedi_citta': '',
      'Clienti_sedi_Province_ID': '',
      'country_sedi': 'IT',
      'richiede_fattura': '',
      'Clienti_sedi_ID_fatt': '', 
      'Clienti_sedi_Nazioni_ID_fatt': '85',
      'Clienti_sedi_ragsociale_fatt': '',
      'Clienti_sedi_PI_fatt': '',
      'Clienti_sedi_indirizzo_fatt': '',
      'Clienti_sedi_numcivico_fatt': '',
      'Clienti_sedi_cap_fatt': '',
      'Clienti_sedi_citta_fatt': '',
      'Clienti_sedi_Province_ID_fatt': '',
      'vettori_ID': '19',
      'coupon_code': '',
      'pagamenti_ID': '58',
      'Clienti_email': ''
}

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
      

      title = utility.getTitleHeader() + "  -  Sotf  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
      utility.setTitle(title)
      mutex.release()

def ScrapeProduct(session, url, prx):

      sizeDict = {}
      articoli_id = ''
      proxy = prx

      print (utility.threadTime('') + utility.bcolors.WARNING + 'Getting product info..' + utility.bcolors.ENDC)
      logging.info('[SOTF] ' + utility.threadTime('') + 'Getting product info..')

      while True:

            try:

                  r = session.get(url, proxies=proxy)
        
                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue
                  
                  soup = BeautifulSoup(r.text.encode('utf-8'), "html.parser")

            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue

            try:
                  articoli_id = soup.find('input', {'name':'articoli_ID'})['value']
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + 'Product out of stock, retrying..')
                  time.sleep(delay)
                  continue

            try:
                  productTitle = soup.find('div', {'class':'details_info_title'}).text

                  productImg = 'https://i.imgur.com/CpewYP8.jpg' #soup.find('a', {'class':'MagicZoom'})['href']

                  for size in soup.find_all('a', {'class':'PdsVariationSelection'}):
                        pid = size['id'].replace('varianti_ID','')
                        sizeID = size.text

                        sizeDict.update({pid:sizeID})
      
                  if len(sizeDict) == 0:
                        print(utility.threadTime('') + utility.bcolors.FAIL + 'Product out of stock, retrying..' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + 'Product out of stock, retrying..')
                        time.sleep(delay)
                        continue
                  else:
                        break
                  
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed getting product info, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed getting product info, retrying..')
                  time.sleep(delay)
                  continue


      return productTitle, productImg, articoli_id, sizeDict, proxy

def AddToCart(session, articoli_id, variant, productURL, prx):

      addToCartPayload = {
            'articoli_ID': articoli_id,
            'documenti_dettaglio[0][articoli_ID]': articoli_id,
            'documenti_dettaglio[0][varianti_ID1]': variant,
            'documenti_dettaglio[0][varianti_ID2]': '0',
            'documenti_dettaglio[0][varianti_ID3]': '0',
            'documenti_dettaglio[0][varianti_ID4]': '0',
            'documenti_dettaglio[0][articoli_quantita]': '1',
            'postback': '1',
            'from_dett': 'false',
            'ajaxMode': 'true'
      }

      headerCF = dict(session.headers)
      headerCF.update({'authority': 'www.sotf.com'})
      headerCF.update({'accept': '/'})
      headerCF.update({'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})
      headerCF.update({'origin': 'https://www.sotf.com/'})
      headerCF.update({'referer': productURL})
      headerCF.update({'x-requested-with': 'XMLHttpRequest'})

      proxy = prx

      while True:
        
            try:

                  r = session.post(url='https://www.sotf.com/it/cart.php', headers=headerCF, data=addToCartPayload, proxies=proxy)
            
                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue

                  soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')

            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue

            try:
                  checkATC = str(soup.find('a', {'href':'https://www.sotf.com/it/cart.php'}).text)
                  if  'VAI AL CARRELLO' in checkATC:
                        print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully added to cart!' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully added to cart!')
                        setTitle(0)
                        break
                  else:
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR 1] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + '[ERROR 1] Failed adding to cart, retrying..')
                        time.sleep(delay)
                        continue
                        
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR 2] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR 2] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue

      return proxy

def Login(session, email, password, prx):

      loginPayload = {
            'logging': '1',
            'from_cart': 'true',
            'clienti_user_name': email,
            'clienti_password': password,
            'button3': 'LOGIN'
      }

      headerCF = dict(session.headers)
      headerCF.update({'authority': 'www.sotf.com'})
      headerCF.update({'cache-control': 'max-age=0'})
      headerCF.update({'upgrade-insecure-requests': '1'})
      headerCF.update({'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9'})
      headerCF.update({'content-type': 'application/x-www-form-urlencoded'})
      headerCF.update({'origin': 'https://www.sotf.com/'})
      headerCF.update({'referer': 'https://www.sotf.com/it/secure/request_account.php?from_cart=true'})

      proxy = prx

      print(utility.threadTime('') + utility.bcolors.WARNING + 'Logging in with: ' + email + utility.bcolors.ENDC)
      logging.info('[SOTF] ' + utility.threadTime('') + 'Logging in with: ' + email)

      while True:
    
            try:

                  r = session.post('https://www.sotf.com/it/login.php', headers=headerCF, data=loginPayload, allow_redirects=True, proxies=proxy)
        
                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue

                  soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')

            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed loggin in, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed loggin in, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed loggin in, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed loggin in, retrying..')
                  time.sleep(delay)
                  continue

            try:

                  indirizzo = soup.find('input', {'name':'Clienti_indirizzo'})['value']
                  sumup_payload.update({'Clienti_indirizzo':indirizzo})

                  numcivico = soup.find('input', {'name':'Clienti_cap'})['value']
                  sumup_payload.update({'Clienti_numcivico':numcivico})

                  cap = soup.find('input', {'name':'Clienti_cap'})['value']
                  sumup_payload.update({'Clienti_cap':cap})

                  citta = soup.find('input', {'name':'Clienti_citta'})['value']
                  sumup_payload.update({'Clienti_citta':citta})

                  tel = soup.find('input', {'name':'Clienti_tel'})['value']
                  sumup_payload.update({'Clienti_tel':tel})

                  provinceID = str(str(soup).split('Seleziona una provincia')[1].split('AUTOCOMPLETE')[0]).split('selected="" value="')[1].split('"')[0]
                  sumup_payload.update({'province_ID':provinceID})
                  sumup_payload.update({'Clienti_sedi_Province_ID':provinceID})
                  sumup_payload.update({'Clienti_sedi_Province_ID_fatt':provinceID})
                  
                  print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully logged in!' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') +  '[' + str(r.status_code) + '] Successfully logged in!')
                  break

            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [TOKEN] Failed during login, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [TOKEN] Failed during login, retrying..')
                  time.sleep(delay)
                  continue

      return proxy

def SetPayPal(session, email, prx):
    
      headerCF = dict(session.headers)
      headerCF.update({'authority': 'www.sotf.com'})
      headerCF.update({'path': '/it/secure/sum_up.php'})
      headerCF.update({'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9'})
      headerCF.update({'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})
      headerCF.update({'upgrade-insecure-requests': '1'})
      headerCF.update({'origin': 'https://www.sotf.com/'})
      headerCF.update({'referer': 'https://www.sotf.com/it/secure/sum_up.php'})

      proxy = prx
      
      print(utility.threadTime('') + utility.bcolors.WARNING + 'Setting PayPal as payment..' + utility.bcolors.ENDC)
      logging.info('[SOTF] ' + utility.threadTime('') + 'Setting PayPal as payment..')

      while True:
        
            try:

                  r = session.post('https://www.sotf.com/it/secure/sum_up.php', headers=headerCF, data=sumup_payload, allow_redirects=True, proxies=proxy)
        
                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue

                  soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')

            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed setting PayPal, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed setting PayPal, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed setting PayPal, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed setting PayPal, retrying..')
                  time.sleep(delay)
                  continue
            
            try:
                  paypalCheck = str(soup.find('input', {'id':'pagamenti_ID58'}))

                  if 'checked' in paypalCheck:
                        print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully set PayPal' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully set PayPal')
                        break
                  else:
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [ID] Failed setting PayPal, retrying..' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + '[ERROR] [ID] Failed setting PayPal, retrying..')
                        time.sleep(delay)
                        continue

            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [HTML PAGE] Failed adding to cart, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [HTML PAGE] Failed adding to cart, retrying..')
                  time.sleep(delay)
                  continue

      return proxy

def Checkout(session, prx):

      headerCF = dict(session.headers)
      headerCF.update({'authority': 'www.sotf.com'})
      headerCF.update({'path': '/it/secure/sum_up.php'})
      headerCF.update({'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9'})
      headerCF.update({'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})
      headerCF.update({'upgrade-insecure-requests': '1'})
      headerCF.update({'origin': 'https://www.sotf.com/'})
      headerCF.update({'referer': 'https://www.sotf.com/it/secure/sum_up.php'})

      proxy = prx

      print(utility.threadTime('') + utility.bcolors.WARNING + 'Completing checkout..' + utility.bcolors.ENDC)
      logging.info('[SOTF] ' + utility.threadTime('') + 'Completing checkout..')

      while True:
        
            try:
                  r = session.post('https://www.sotf.com/it/check_out.php', headers=headerCF, data=sumup_payload, allow_redirects=True, proxies=proxy)
        
                  if str(r.status_code) == '503':
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ACCESS DENIED] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(r.status_code) + '] [ACCESS DENIED] Proxy banned, retrying with a new one..')
                        proxy = GetNewProxy()
                        time.sleep(delay)
                        continue

                  soup = BeautifulSoup(r.text.encode('utf-8'), 'html.parser')

            except requests.exceptions.ProxyError as errp:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[PROXY ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errp) + '] [PROXY ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.ConnectionError as errh:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[CONNECTION ERROR] Proxy banned, retrying with a new one..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errh) + '] [CONNECTION ERROR] Proxy banned, retrying with a new one..')
                  proxy = GetNewProxy()
                  time.sleep(delay)
                  continue
            except requests.exceptions.Timeout as errt:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[TIMEOUT] Failed completing checkout, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(errt) + '] [TIMEOUT] Failed completing checkout, retrying..')
                  time.sleep(delay)
                  continue
            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] Failed completing checkout, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] Failed completing checkout, retrying..')
                  time.sleep(delay)
                  continue

            try:
                  checkout = str(soup.find('meta', {'http-equiv':'refresh'})['content']).split('url=')[1]

                  if 'paypal' in checkout:
                        print(utility.threadTime('') + utility.bcolors.OKGREEN + '[' + str(r.status_code) + '] Successfully checked out!' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(r.status_code) + '] Successfully checked out!')
                        setTitle(1)
                        break
                  else:
                        print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [OOS] Failed checking out, retrying..' + utility.bcolors.ENDC)
                        logging.info('[SOTF] ' + utility.threadTime('') + '[ERROR] [OOS] Failed checking out, retrying..')
                        time.sleep(delay)
                        continue

            except Exception as e:
                  print(utility.threadTime('') + utility.bcolors.FAIL + '[ERROR] [HTML PAGE] Failed checking out, retrying..' + utility.bcolors.ENDC)
                  logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] [ERROR] [HTML PAGE] Failed checking out, retrying..')
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


def main(url, size, email, password):

      SetupCloudscraper()
            
      sumup_payload.update({'Clienti_email':email})

      prx = GetNewProxy()

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

      while True:
            productTitle, productIMG, articoli_id, sizeList, prx = ScrapeProduct(s, url, prx)
            variant, sizeID = utility.SelectSize(sizeList, size, '', 'SOTF', configDict)

            if variant != -1 and sizeID != 1:
                  break

      start_time = datetime.now()

      print(utility.threadTime('') + utility.bcolors.WARNING + 'Adding to cart size ['+sizeID+']' + utility.bcolors.ENDC)
      logging.info('[SOTF] ' + utility.threadTime('') + 'Adding to cart size ['+sizeID+']')

      prx = AddToCart(s, articoli_id, variant, url, prx)
      prx = Login(s, email, password, prx)

      prx = SetPayPal(s, email, prx)
      checkoutURL = Checkout(s, prx)
      final_time = datetime.now()-start_time

      try:
            link = utility.getCheckoutLink(s, 'https://www.sotf.com/', checkoutURL)
      except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed getting checkout link with cookie!' + utility.bcolors.ENDC)
            logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] Failed getting checkout link with cookie!')
            time.sleep(100)    

      crissWebhook.sendWebhook('Sotf', url, email, productTitle, sizeID, link, productIMG, 'PayPal', final_time)
      crissWebhook.publicWebhook('Sotf', url, productTitle, sizeID, productIMG, final_time, 'PayPal')
      crissWebhook.staffWebhook('Sotf', productTitle, sizeID, productIMG, str(final_time))

      input('')
      time.sleep(100)

def shockdrop(URL, val):

      title = utility.getTitleHeader() + "  -  Sotf  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
      utility.setTitle(title)

      accountDict = {}

      try:
            global allProxies
            allProxies = utility.loadProxies('sotf')
            with open('sotf/task.csv', 'r') as csv_file:
                  csv_key = csv.DictReader(csv_file)

                  for line in csv_key:
                        try:
                              for tasks in range(0, val):
                                    t = Thread(target=main, args=(URL, 'RANDOM', line['EMAIL'], line['PASSWORD']))
                                    t.start()
                              
                              break
                        
                        except Exception as e:
                              print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                              logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                              input('Press ENTER to exit.')
                              sys.exit()
      except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
            logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
            input('Press ENTER to exit.')
            sys.exit()

def start_main():

      title = utility.getTitleHeader() + "  -  Sotf  -  Carted: " + str(carted) + "  /  Checkout: " + str(checkouted)
      utility.setTitle(title)

      try:
            global allProxies
            allProxies = utility.loadProxies('sotf')
            with open('sotf/task.csv', 'r') as csv_file:
                  csv_key = csv.DictReader(csv_file)

                  for line in csv_key:
                        try:
                              t = Thread(target=main, args=(line['URL'], line['SIZE'], line['EMAIL'], line['PASSWORD']))
                              t.start()
                        except Exception as e:
                              print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
                              logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
                              input('Press ENTER to exit.')
                              sys.exit()
      except Exception as e:
            print(utility.threadTime('') + utility.bcolors.FAIL + 'Failed loading task, please check csv file!' + utility.bcolors.ENDC)
            logging.info('[SOTF] ' + utility.threadTime('') + '[' + str(e) + '] Failed loading task, please check csv file!')
            input('Press ENTER to exit.')
            sys.exit()

if __name__ == '__main__':
    start_main()