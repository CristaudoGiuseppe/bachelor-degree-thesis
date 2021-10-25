# ------------------------------------------------------------------------------- #

from utils import extract_domain, compressToEncodedURIComponent, check_for_captcha
import re, base64, time, requests, utility
import importlib
import urllib3
from bs4 import BeautifulSoup

# ------------------------------------------------------------------------------- #

class CF_2():
    def __init__(self, adapter, original, key, captcha=False, debug=False):
        # Config vars
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.script = "https://{}/cdn-cgi/challenge-platform/orchestrate/jsch/v1"
        self.captcha_script = "https://{}/cdn-cgi/challenge-platform/orchestrate/captcha/v1"
        self.api_domain = "cf-v2.hwkapi.com"

        self.timeOut = 30
        self.errorDelay = 0

        # Vars
        self.adapter = adapter
        self.original_request = original
        self.domain = extract_domain(original.url)
        self.debug = debug
        self.key = key
        self.auth_params = {
            "auth": self.key
        }

        self.captcha = captcha

        self.start_time = time.time()

    def solve(self):
        """Loading init script"""

        self.solveRetries = 0
        self.solveMaxRetries = 5
        while True:
            if self.debug:
                print(utility.threadTime('CF') + utility.bcolors.WARNING + f'Solving CF challenge ({self.solveRetries}/{self.solveMaxRetries})' + utility.bcolors.ENDC)

            if self.solveRetries == self.solveMaxRetries:

                raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + f"Solving challenge failed after {self.solveMaxRetries} retries." + utility.bcolors.ENDC)
            else:
                self.solveRetries += 1

                # Fetching CF script
                if not self.captcha:
                    script = self.script.format(self.domain)
                else:
                    script = self.captcha_script.format(self.domain)

                try:
                    self.init_script = self.adapter.get(script, timeout=self.timeOut)
                except Exception as e:
                    if self.debug:
                        print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Failed to request init script: {str(e)}" + utility.bcolors.ENDC)
                    time.sleep(self.errorDelay)
                    continue
                else:
                    #if self.debug:
                    #    print(utility.threadTime('CF') + utility.bcolors.OKGREEN + "Loaded initiat script" + utility.bcolors.ENDC)

                    self.solveRetries = 0
                    return self.challenge_initation_payload()

    def challenge_initation_payload(self):
        """Fetches payload for challenge iniation from our api"""

        self.initPayloadRetries = 0
        self.initPayloadMaxRetries = 5
        while True:
            #if self.debug:
            #    print(utility.threadTime('CF') + utility.bcolors.WARNING + f"Fetching payload ({self.initPayloadRetries}/{self.initPayloadMaxRetries})" + utility.bcolors.ENDC)

            if self.initPayloadRetries == self.initPayloadMaxRetries:
                raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + f"Fetching payload failed after {self.initPayloadMaxRetries} retries" + utility.bcolors.ENDC)
            else:
                self.initPayloadRetries += 1

                # Parsing of the data needed for the api to serve the init payload
                try:
                    matches = re.findall(r"0\.[^('|/)]+", self.init_script.text)
                    urlpart = matches[0]
                    matches = re.findall(r"[\W]?([A-Za-z0-9+\-$]{65})[\W]", self.init_script.text)
                    for i in matches:
                        i = i.replace(",", "" + utility.bcolors.ENDC)
                        if "+" in i and "-" in i and "$" in i:
                            self.keyStrUriSafe = i
                            break
                except Exception as e:
                    if self.debug:
                        print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Failed to parse data needed for init payload: {str(e)}" + utility.bcolors.ENDC)
                    time.sleep(self.errorDelay)
                    continue

                # Requesting payload from the api
                try:
                    payload = {
                        "body": base64.b64encode(self.original_request.text.encode("UTF-8")).decode("UTF-8"),
                        "url": urlpart,
                        "domain": self.domain,
                        "captcha": self.captcha
                    }
                    challenge_payload = requests.post("https://{}/cf-a/ov1/p1".format(self.api_domain),
                                                      params=self.auth_params, json=payload, verify=False,
                                                      timeout=self.timeOut).json()
                    self.init_url = challenge_payload["url"]
                    self.request_url = challenge_payload["result_url"]
                    self.result = challenge_payload["result"]
                    self.name = challenge_payload["name"]
                    self.baseobj = challenge_payload["baseobj"]
                    self.request_pass = challenge_payload["pass"]
                    self.request_r = challenge_payload["r"]
                    self.ts = challenge_payload["ts"]
                except Exception as e:
                    if self.debug:
                        #checkare la chiave
                        print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Failed submit data to the api: {str(e)}, propably API down" + utility.bcolors.ENDC)
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.initPayloadRetries = 0

                    #if self.debug:
                    #    print(utility.threadTime('CF') + utility.bcolors.OKGREEN + "Submitted initial payload to the api" + utility.bcolors.ENDC)

                    return self.initiate_cloudflare()

    def initiate_cloudflare(self):
        """Initiares the cloudflare challenge"""

        self.initChallengeRetries = 0
        self.initChallengeMaxRetries = 5
        while True:
            #if self.debug:
            #    print(utility.threadTime('CF') + utility.bcolors.WARNING + f"Initiating challenge. ({self.initChallengeRetries}/{self.initChallengeMaxRetries})" + utility.bcolors.ENDC)

            if self.initChallengeRetries == self.initChallengeMaxRetries:
                raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + f"Initiating challenge failed after {self.initChallengeMaxRetries} retries." + utility.bcolors.ENDC)
            else:
                self.initChallengeRetries += 1

                if not self.keyStrUriSafe:
                    raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + "KeyUri cannot be None." + utility.bcolors.ENDC)
                else:
                    try:
                        payload = {
                            self.name: compressToEncodedURIComponent(base64.b64decode(self.result).decode(),
                                                                     self.keyStrUriSafe)
                        }

                        self.adapter.headers["cf-challenge"] = self.init_url.split("/" + utility.bcolors.ENDC)[-1]
                        self.adapter.headers["referer"] = self.original_request.url.split("?" + utility.bcolors.ENDC)[0]
                        self.adapter.headers["origin"] = f"https://{self.domain}"
                        self.challenge_payload = self.adapter.post(self.init_url, data=payload, timeout=self.timeOut)
                    except Exception as e:
                        if self.debug:
                            print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Initiating challenge error: {str(e)}" + utility.bcolors.ENDC)
                        time.sleep(self.errorDelay)
                        continue
                    else:
                        self.initChallengeRetries = 0

                        #if self.debug:
                        #    print(utility.threadTime('CF') + utility.bcolors.OKGREEN + "Initiated challenge." + utility.bcolors.ENDC)

                        return self.solve_payload()

    def solve_payload(self):
        """Fetches main challenge payload from hawk api"""

        self.fetchingChallengeRetries = 0
        self.fetchingChallengeMaxRetries = 5
        while True:
            #if self.debug:
            #    print(utility.threadTime('CF') + utility.bcolors.WARNING + f"Fetching main challenge. ({self.fetchingChallengeRetries}/{self.fetchingChallengeMaxRetries})" + utility.bcolors.ENDC)

            if self.fetchingChallengeRetries == self.fetchingChallengeMaxRetries:
                raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + f"Fetching main challenge failed after {self.fetchingChallengeMaxRetries} retries. This error ist mostlikly related to a wrong usage of headers" + utility.bcolors.ENDC)
            else:
                self.fetchingChallengeRetries += 1

                try:
                    payload = {
                        "body_home": base64.b64encode(self.original_request.text.encode()).decode(),
                        "body_sensor": base64.b64encode(self.challenge_payload.text.encode()).decode(),
                        "result": self.baseobj,
                        "ts": self.ts,
                        "url": self.init_url,
                    }

                    cc = requests.post("https://{}/cf-a/ov1/p2".format(self.api_domain), verify=False,
                                       params=self.auth_params, json=payload, timeout=self.timeOut)
                    cc = cc.json()
                    self.result = cc["result"]
                except Exception as e:
                    if self.debug:
                        print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Fetching challenge payload error: {str(e)}" + utility.bcolors.ENDC)
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.fetchingChallengeRetries = 0

                    #if self.debug:
                    #    print(utility.threadTime('CF') + utility.bcolors.OKGREEN + "Fetched challenge payload." + utility.bcolors.ENDC)

                    return self.send_main_payload()

    def send_main_payload(self):
        """Sends the main payload to cf"""

        self.submitChallengeRetries = 0
        self.submitChallengeMaxRetries = 5
        while True:
            #if self.debug:
            #    print(utility.threadTime('CF') + utility.bcolors.WARNING + f"Submitting challenge. ({self.submitChallengeRetries}/{self.submitChallengeMaxRetries})" + utility.bcolors.ENDC)

            if self.submitChallengeRetries == self.submitChallengeMaxRetries:
                raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + f"Submitting challenge failed after {self.submitChallengeMaxRetries} retries." + utility.bcolors.ENDC)
            else:
                self.submitChallengeRetries += 1

                try:
                    payload = {
                        self.name: compressToEncodedURIComponent(base64.b64decode(self.result).decode(),
                                                                 self.keyStrUriSafe)
                    }
                    self.mainpayload_response = self.adapter.post(self.init_url, data=payload, timeout=self.timeOut)
                except Exception as e:
                    if self.debug:
                        print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Submitting challenge error: {str(e)}" + utility.bcolors.ENDC)
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.submitChallengeRetries = 0

                    #if self.debug:
                    #    print(utility.threadTime('CF') + utility.bcolors.OKGREEN + "Submitted challenge." + utility.bcolors.ENDC)

                    return self.getChallengeResult()

    def getChallengeResult(self):
        """Fetching challenge result"""

        self.challengeResultRetries = 0
        self.challengeResultMaxRetries = 5
        while True:
            #if self.debug:
            #    print(utility.threadTime('CF') + utility.bcolors.WARNING + f"Fetching challenge result. ({self.challengeResultRetries}/{self.challengeResultMaxRetries})" + utility.bcolors.ENDC)

            if self.challengeResultRetries == self.challengeResultMaxRetries:
                raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + f"Fetching challenge result failed after {self.challengeResultMaxRetries} retries." + utility.bcolors.ENDC)
            else:
                self.challengeResultRetries += 1

                try:
                    payload = {
                        "body_sensor": base64.b64encode(self.mainpayload_response.text.encode()).decode(),
                        "result": self.baseobj
                    }

                    ee = requests.post("https://{}/cf-a/ov1/p3".format(self.api_domain), verify=False,
                                       params=self.auth_params, json=payload, timeout=self.timeOut)
                    self.final_api = ee.json()
                except Exception as e:
                    if self.debug:
                        print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Fetching challenge result error: {str(e)}" + utility.bcolors.ENDC)
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.challengeResultRetries = 0

                    #if self.debug:
                    #    print(utility.threadTime('CF') + utility.bcolors.OKGREEN + "Fetched challenge response." + utility.bcolors.ENDC)

                    return self.handle_final_api()

    def handle_final_api(self):
        """Handle final API result and rerun if needed"""

        if self.final_api["status"] == "rerun":
            return self.handle_rerun()
        if self.final_api["captcha"]:
            if not self.captcha:
                raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + "CF returned captcha and captcha handling is disabled" + utility.bcolors.ENDC)
            else:
                return self.handle_captcha()
        else:
            return self.submit()

    def submit(self):
        """Submits the challenge and trys to access target url"""

        self.submitFinalChallengeRetries = 0
        self.submitFinalChallengeMaxRetries = 5
        while True:
            #if self.debug:
            #    print(utility.threadTime('CF') + utility.bcolors.WARNING + f"Submitting final challenge. ({self.submitFinalChallengeRetries}/{self.submitFinalChallengeMaxRetries})" + utility.bcolors.ENDC)

            if self.submitFinalChallengeRetries == self.submitFinalChallengeMaxRetries:
                raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + f"Submitting final challenge failed after {self.submitFinalChallengeMaxRetries} retries." + utility.bcolors.ENDC)
            else:
                self.submitFinalChallengeRetries += 1

                self.adapter.headers["referer"] = self.original_request.url
                self.adapter.headers["origin"] = f"https://{self.domain}"

                try:
                    payload = {
                        "r": self.request_r,
                        "jschl_vc": self.final_api["jschl_vc"],
                        "pass": self.request_pass,
                        "jschl_answer": self.final_api["jschl_answer"],
                        "cf_ch_verify": "plat"
                    }

                    # cf added a new flow where they present a 503 followed up by a 403 captcha
                    if "cf_ch_cp_return" in self.final_api:
                        self.captcha = True
                        payload["cf_ch_cp_return"] = self.final_api["cf_ch_cp_return"]

                    if round(time.time() - self.start_time) < 5:
                        # Waiting X amount of sec for CF delay
                        if self.debug:
                            print(utility.threadTime('CF') + utility.bcolors.WARNING + "Sleeping {} sec for CF delay".format(5 - round(time.time() - self.start_time)) +utility.bcolors.ENDC)
                        time.sleep(5 - (round(time.time() - self.start_time)))

                    final = self.adapter.post(self.request_url, data=payload, timeout=self.timeOut)
                except Exception as e:
                    if self.debug:
                        print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Submitting final challenge error: {str(e)}" + utility.bcolors.ENDC)
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.submitFinalChallengeRetries = 0

                    #if self.debug:
                    #    print(utility.threadTime('CF') + utility.bcolors.OKGREEN + "Submitted final challange." + utility.bcolors.ENDC)

                    if final.status_code == 403:
                        soup = BeautifulSoup(final.text, "lxml" + utility.bcolors.ENDC)
                        if check_for_captcha(soup):
                            # as this was a 403 post we need to get again dont ask why just do it
                            weird_get_req = self.adapter.get(self.original_request.url,timeout=self.timeOut)
                            return CF_2(self.adapter, weird_get_req, self.key,True,self.debug).solve()

                    return final

    def handle_rerun(self):
        """Handling rerun"""

        self.rerunRetries = 0
        self.rerunMaxRetries = 5
        while True:
            #if self.debug:
            #    print(utility.threadTime('CF') + utility.bcolors.WARNING + f"Handling rerun. ({self.rerunRetries}/{self.rerunMaxRetries})" + utility.bcolors.ENDC)

            if self.rerunRetries == self.rerunMaxRetries:
                raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + f"Rerun failed after {self.rerunMaxRetries} retries." + utility.bcolors.ENDC)
            else:
                self.rerunRetries += 1

                try:
                    payload = {
                        "body_home": base64.b64encode(self.original_request.text.encode()).decode(),
                        "body_sensor": base64.b64encode(self.mainpayload_response.text.encode()).decode(),
                        "result": self.baseobj,
                        "ts": self.ts,
                        "url": self.init_url,
                        "rerun": True,
                        "rerun_base": self.result
                    }
                    alternative = requests.post("https://{}/cf-a/ov1/p2".format(self.api_domain), verify=False,
                                                params=self.auth_params, json=payload, timeout=self.timeOut)
                    alternative = alternative.json()
                    self.result = alternative["result"]
                except Exception as e:
                    if self.debug:
                        print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Fetching rerun challenge payload error: {str(e)}" + utility.bcolors.ENDC)
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.rerunRetries = 0

                    #if self.debug:
                    #    print(utility.threadTime('CF') + utility.bcolors.OKGREEN + "Handled rerun." + utility.bcolors.ENDC)

                    return self.send_main_payload()

    def handle_captcha(self):
        """Handling captcha"""

        self.captchaRetries = 0
        self.captchaMaxRetries = 5
        while True:
            if self.debug:
                print(utility.threadTime('CF') + utility.bcolors.WARNING + f"Handling captcha. ({self.captchaRetries}/{self.captchaMaxRetries})" + utility.bcolors.ENDC)

            if self.captchaRetries == self.captchaMaxRetries:
                raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + f"Handling captcha failed after {self.captchaMaxRetries} retries." + utility.bcolors.ENDC)
            else:
                self.captchaRetries += 1
                if self.final_api["click"]:
                    token = "click"
                else:
                    if self.debug:
                        print(utility.threadTime('CF') + utility.bcolors.WARNING + "HCaptcha needed, requesting token.." + utility.bcolors.ENDC)
                    try:
                        # ------------------------------------------------------------------------------- #
                        # Pass proxy parameter to provider to solve captcha.
                        # ------------------------------------------------------------------------------- #

                        if self.adapter.proxies and self.adapter.proxies != self.adapter.captcha.get('proxy'):
                            self.adapter.captcha['proxy'] = self.adapter.proxies

                        # ------------------------------------------------------------------------------- #
                        # Pass User-Agent if provider supports it to solve captcha.
                        # ------------------------------------------------------------------------------- #

                        self.adapter.captcha['User-Agent'] = self.adapter.headers['User-Agent']

                        TwoCap = importlib.import_module('cloudscraper.captcha.2captcha').captchaSolver()
                        token = TwoCap.getCaptchaAnswer(
                            "hCaptcha",
                            self.original_request.url,
                            self.final_api["sitekey"],
                            self.adapter.captcha
                        )
                    except Exception as e:
                        if self.debug:
                            print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Failed to get Captcha Token from 2Captcha.." + utility.bcolors.ENDC) #{str(e)}
                    else:
                        if self.debug:
                            print(utility.threadTime('CF') + utility.bcolors.OKGREEN + f"Got Captcha Token from 2Captcha!" + utility.bcolors.ENDC)

                try:
                    payload = {
                        "result": self.result,
                        "token": token,
                        "h-captcha-response": token,
                        "data": self.final_api["result"]
                    }

                    # first captcha api call
                    ff = requests.post("https://{}/cf-a/ov1/cap1".format(self.api_domain), verify=False,
                                       params=self.auth_params, json=payload, timeout=self.timeOut)
                    self.first_captcha_result = ff.json()
                except Exception as e:
                    if self.debug:
                        print(utility.threadTime('CF') + utility.bcolors.FAIL + f"First captcha API call error: {str(e)}" + utility.bcolors.ENDC)
                    time.sleep(self.errorDelay)
                    continue
                else:
                    try:
                        payload = {
                            self.name: compressToEncodedURIComponent(
                                base64.b64decode(self.first_captcha_result["result"]).decode(), self.keyStrUriSafe)
                        }
                        self.adapter.headers["referer"] = self.original_request.url
                        self.adapter.headers["origin"] = self.domain
                        self.adapter.headers["cf-challenge"] = self.init_url.split("/" + utility.bcolors.ENDC)[-1]

                        gg = self.adapter.post(self.init_url, data=payload, timeout=self.timeOut)
                    except Exception as e:
                        if self.debug:
                            print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Posting to CloudFlare challenge endpoint error: {str(e)}" + utility.bcolors.ENDC)
                        time.sleep(self.errorDelay)
                        continue
                    else:
                        try:
                            payload = {
                                "body_sensor": base64.b64encode(gg.text.encode()).decode(),
                                "result": self.baseobj
                            }

                            hh = requests.post("https://{}/cf-a/ov1/cap2".format(self.api_domain),
                                               params=self.auth_params, json=payload, verify=False,
                                               timeout=self.timeOut)
                            self.captcha_response_api = hh.json()
                        except Exception as e:
                            if self.debug:
                                print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Second captcha API call error: {str(e)}" + utility.bcolors.ENDC)
                            time.sleep(self.errorDelay)
                            continue
                        else:
                            self.captchaRetries = 0
                            if self.captcha_response_api["valid"]:
                                if self.debug:
                                    print(utility.threadTime('CF') + utility.bcolors.OKGREEN + "Captcha accepted!" + utility.bcolors.ENDC)
                                return self.submit_captcha()
                            else:
                                print(utility.threadTime('CF') + utility.bcolors.FAIL + "Captcha was not accepted.." + utility.bcolors.ENDC)

    def submit_captcha(self):
        """Submits the challenge + captcha and trys to access target url"""

        self.submitCaptchaRetries = 0
        self.submitCaptchaMaxRetries = 5
        while True:
            #if self.debug:
            #    print(utility.threadTime('CF') + utility.bcolors.WARNING + f"Submitting captcha challenge. ({self.submitCaptchaRetries}/{self.submitCaptchaMaxRetries})" + utility.bcolors.ENDC)

            if self.submitCaptchaRetries == self.submitCaptchaMaxRetries:
                raise Exception(utility.threadTime('CF') + utility.bcolors.FAIL + f"Submitting captcha challenge failed after {self.submitCaptchaMaxRetries} retries." + utility.bcolors.ENDC)
            else:
                self.submitCaptchaRetries += 1

                try:
                    self.adapter.headers["referer"] = self.original_request.url
                    self.adapter.headers["origin"] = f"https://{self.domain}"

                    payload = {
                        "r": self.request_r,
                        "cf_captcha_kind": "h",
                        "vc": self.request_pass,
                        "captcha_vc": self.captcha_response_api["jschl_vc"],
                        "captcha_answer": self.captcha_response_api["jschl_answer"],
                        "cf_ch_verify": "plat",
                        "h-captcha-response": "captchka"
                    }

                    if round(time.time() - self.start_time) < 5:
                        # Waiting X amount of sec for CF delay
                        if self.debug:
                            print(utility.threadTime('CF') + utility.bcolors.WARNING + "Sleeping {} sec for CF delay".format(5 - round(time.time() - self.start_time)))
                        time.sleep(5 - (round(time.time() - self.start_time)))

                    final = self.adapter.post(self.request_url, data=payload, timeout=self.timeOut)
                except Exception as e:
                    if self.debug:
                        print(utility.threadTime('CF') + utility.bcolors.FAIL + f"Submitting captcha challenge error: {str(e)}" + utility.bcolors.ENDC)
                    time.sleep(self.errorDelay)
                    continue
                else:
                    self.submitCaptchaRetries = 0

                    if self.debug:
                        print(utility.threadTime('CF') + utility.bcolors.OKGREEN + "Solved CF captcha challange!" + utility.bcolors.ENDC)

                    return final
