import json
import re
import time
import names
import requests
import tls_client
import os
import random
import secrets
import datetime
import threading

from tls_client.exceptions import TLSClientExeption
from bs4 import BeautifulSoup
from colorama import Fore


os.system("")

# Input your https://dashboard.capsolver.com/passport/register?inviteCode=LyJfsyi3ypCa API Key in the field below.
CAPSOLVER_KEY = "CAP-"

with open("proxies.txt", "r") as p:
    proxies = p.read().splitlines()

end_gen = False
thread_lock = threading.Lock()
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


class Utils:

    @staticmethod
    def fetch_email():
        response = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
        if response.status_code == 200:
            email = response.json()[0]
            return email
        else:
            return Utils.fetch_email()

    @staticmethod
    def solve_recaptcha(page_action):
        task_payload = {
            "clientKey": CAPSOLVER_KEY,
            "task": {
                "type": "ReCaptchaV3TaskProxyLess",
                "websiteURL": "https://in.alienwarearena.com/",
                "websiteKey": "6LfRnbwaAAAAAPYycaGDRhoUqR-T0HyVwVkGEnmC",
                "pageAction": page_action,
                "userAgent": user_agent,
                "AppID": "C10FB33E-8CED-4F6D-990C-356E42F5E318"
            }
        }

        response = requests.post("https://api.capsolver.com/createTask", json=task_payload)
        if response.status_code == 200:
            task_id = response.json()["taskId"]
        else:
            raise Exception(f"Failed to create captcha task | {response.text}")

        solution_payload = {
            "clientKey": CAPSOLVER_KEY,
            "taskId": task_id
        }

        while True:
            response = requests.post("https://api.capsolver.com/getTaskResult", json=solution_payload)
            if "ready" in response.text:
                return response.json()["solution"]["gRecaptchaResponse"]
            elif "processing" in response.text:
                time.sleep(1)
                continue
            else:
                raise Exception("Failed to solve captcha.")

    @staticmethod
    def extract_token(html, name):
        soup = BeautifulSoup(html, 'html.parser')
        token = soup.find('input', {'name': name}).get('value')
        return token

    @staticmethod
    def extract_link(html):
        soup = BeautifulSoup(html, 'html.parser')
        activation_link = soup.find('a', class_='mcnButton')['href']
        return activation_link

    @staticmethod
    def extract_verification_link(user, domain):
        count = int()
        while count < 300:
            response = requests.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={user}&domain={domain}")
            if "Activate Your Alienware Arena Account" in response.text:
                for message in response.json():
                    if message["subject"] == "Activate Your Alienware Arena Account":
                        message_id = message["id"]
                        response = requests.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={user}&domain={domain}&id={message_id}")
                        if response.status_code == 200:
                            message_content = response.json()["body"]
                            return Utils.extract_link(message_content)
            else:
                count += 1
                time.sleep(1)


class Logger:
    @staticmethod
    def info(content):
        print(
            f'{Fore.LIGHTBLACK_EX}[{datetime.datetime.now().strftime("%I:%M:%S %p")}] {Fore.GREEN}{content}{Fore.RESET}'
        )

    @staticmethod
    def error(content):
        print(
            f'{Fore.LIGHTBLACK_EX}[{datetime.datetime.now().strftime("%I:%M:%S %p")}] {Fore.RED}{content}{Fore.RESET}'
        )

    @staticmethod
    def inp(content):
        return (
            f'{Fore.LIGHTBLACK_EX}[{datetime.datetime.now().strftime("%I:%M:%S %p")}] {Fore.CYAN}{content}{Fore.RESET}'
        )


class GeneratePromo:

    def __init__(self):
        self.session = tls_client.Session(
            client_identifier="chrome_122"
        )
        self.session.timeout_seconds = 30

        proxy = random.choice(proxies)
        self.session.proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

        self.page_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "in.alienwarearena.com",
            "Origin": "https://in.alienwarearena.com",
            "Referer": "https://in.alienwarearena.com/account/register",
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": user_agent
        }

        self.email_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Host": "mandrillapp.com",
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }

        self.key_headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Host": "giveawayapi.alienwarearena.com",
            "Origin": "https://in.alienwarearena.com",
            "Referer": "https://in.alienwarearena.com/",
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": user_agent
        }

        self.request_headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Host": "in.alienwarearena.com",
            "Referer": "https://in.alienwarearena.com/ucf/show/2170237/boards/contest-and-giveaways-global/one-month-of-discord-nitro-exclusive-key-giveaway",
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": user_agent,
            "X-Requested-With": "XMLHttpRequest"
        }

        self.email = Utils.fetch_email()

    def register_account(self) -> bool:

        try:
            response = self.session.get("https://in.alienwarearena.com/account/register", headers=self.page_headers)
        except TLSClientExeption:
            return self.register_account()

        token = Utils.extract_token(response.content, "user_registration[_token]")

        data = {
            "user_registration[email][first]": self.email,
            "user_registration[email][second]": self.email,
            "user_registration[birthdate][month]": str(random.randint(1, 12)),
            "user_registration[birthdate][day]": str(random.randint(1, 28)),
            "user_registration[birthdate][year]": str(random.randint(1970, 2004)),
            "user_registration[termsAccepted]": "1",
            "user_registration[_token]": token,
            "user_registration[steamId]": "",
            "user_registration[battlenetOauthProfileId]": "",
            "user_registration[timezone]": "Asia/Kolkata",
            "user_registration[sourceInfo]": None,
            "user_registration[referralCode]": "",
            "user_registration[recaptcha3]": Utils.solve_recaptcha("registration")
        }

        try:
            response = self.session.post("https://in.alienwarearena.com/account/register", headers=self.page_headers, data=data, allow_redirects=True)
        except TLSClientExeption:
            return self.register_account()

        if response.url != "https://in.alienwarearena.com/account/check-email":
            try:
                error = response.text.split('class="form-error-message">')[1].split('</span>')[0]
            except Exception:
                raise Exception(f"Failed to register account | {self.email}")

            raise Exception(f"Failed to register account | {self.email} | {error.strip()}")

        else:
            return True

    def verify_email(self, verification_link: str) -> bool:
        self.session.cookies.clear()

        try:
            response = self.session.get(verification_link, headers=self.email_headers)
            response = self.session.get(response.headers["Location"], headers=self.page_headers)
        except TLSClientExeption:
            return self.verify_email(verification_link)

        token = Utils.extract_token(response.content, "platformd_user_confirm_registration[_token]")
        data = {
            "platformd_user_confirm_registration[confirm]": "",
            "platformd_user_confirm_registration[_token]": token
        }
        try:
            response = self.session.post(response.url, headers=self.page_headers, data=data)
        except TLSClientExeption:
            return self.verify_email(verification_link)

        if response.status_code == 302:
            return True
        else:
            raise Exception(f"Failed to verify e-mail | {self.email}")

    def set_password(self):
        try:
            response = self.session.get("https://in.alienwarearena.com/incomplete", headers=self.page_headers)
        except TLSClientExeption:
            return self.set_password()

        token = Utils.extract_token(response.content, "platformd_incomplete_account[_token]")

        password = secrets.token_hex(6)
        data = {
            "platformd_incomplete_account[username]": secrets.token_hex(5),
            "platformd_incomplete_account[password][first]": password,
            "platformd_incomplete_account[password][second]": password,
            "platformd_incomplete_account[_token]": token
        }

        try:
            self.session.post("https://in.alienwarearena.com/incomplete", headers=self.page_headers, data=data, allow_redirects=True)
        except TLSClientExeption:
            return self.set_password()

    def complete_profile(self) -> bool:

        try:
            response = self.session.get("https://in.alienwarearena.com/incomplete", headers=self.page_headers)
        except TLSClientExeption:
            return self.complete_profile()

        token = Utils.extract_token(response.content, "platformd_incomplete_account[_token]")
        data = {
            "platformd_incomplete_account[firstname]": names.get_first_name(),
            "platformd_incomplete_account[lastname]": names.get_last_name(),
            "platformd_incomplete_account[country]": "IN",
            "platformd_incomplete_account[state]": "1291",
            "platformd_incomplete_account[preferredGenre]": "action",
            "platformd_incomplete_account[_token]": token
        }

        try:
            response = self.session.post("https://in.alienwarearena.com/incomplete", headers=self.page_headers, data=data, allow_redirects=True)
        except TLSClientExeption:
            return self.complete_profile()

        if response.status_code == 200:
            return True
        else:
            raise Exception(f"Failed to complete registration | {self.email}")


    def get_promo_details(self) -> tuple:
        try:
            response = self.session.get("https://in.alienwarearena.com/ucf/show/2170237/boards/contest-and-giveaways-global/one-month-of-discord-nitro-exclusive-key-giveaway", headers=self.page_headers)
        except TLSClientExeption:
            return self.get_promo_details()

        user_id_match = re.search(r'var user_id\s*=\s*(\d+);', response.text)
        user_uuid_match = re.search(r'var user_uuid\s*=\s*"(.*?)";', response.text)
        user_country_match = re.search(r'var user_country\s*=\s*"(.*?)";', response.text)
        login_id_match = re.search(r'var login_id\s*=\s*(\d+);', response.text)

        user_id = int(user_id_match.group(1)) if user_id_match else None
        user_uuid = user_uuid_match.group(1) if user_uuid_match else None
        user_country = user_country_match.group(1) if user_country_match else "IN"
        login_id = int(login_id_match.group(1)) if login_id_match else None

        return user_id, user_uuid, user_country, login_id

    def extract_promo_key(self, user_id: int, user_uuid: str, user_country: str, login_id: int) -> bool:
        params = {
            "giveaway_uuid": "df863897-304c-4985-830c-56414830ade7",
            "api_key": "a75eb2f0-3f7a-4742-96c7-202977acb4cf",
            "user_uuid": user_uuid,
            "recaptcha_token": Utils.solve_recaptcha("getkey"),
            "extra_info": json.dumps({
                "siteId": 7,
                "siteGroupId": 1,
                "loginId": login_id,
                "countryCode": user_country,
                "userId": user_id
            })
        }
        try:
            response = self.session.get("https://giveawayapi.alienwarearena.com/production/key/get", headers=self.key_headers, params=params)
        except TLSClientExeption:
            return self.extract_promo_key(user_id, user_uuid, user_country, login_id)

        if response.status_code == 200:
            return True
        else:
            raise Exception(f"Failed to get promo key | {self.email} | " + response.json()["errorMessage"])

    def get_promo_key(self) -> str:
        try:
            response = self.session.get("https://in.alienwarearena.com/giveaways/keys", headers=self.request_headers)
        except TLSClientExeption:
            return self.get_promo_key()

        if response.status_code == 200:
            return response.json()[0]["value"]
        else:
            raise Exception(f"Failed to get promo code | {self.email}.")

    def generate_promo(self, thread_id) -> None:
        global end_gen

        try:
            self.register_account()
            Logger.info(
                f"[{thread_id}] Successfully created account | {self.email}."
            )
            time.sleep(1)
            verification_link = Utils.extract_verification_link(
                user=self.email.split("@")[0],
                domain=self.email.split("@")[1]
            )
            self.verify_email(verification_link)

            Logger.info(
                f"[{thread_id}] Successfully verified account | {self.email}."
            )
            self.set_password()
            self.complete_profile()

            Logger.info(
                f"[{thread_id}] Successfully completed account profile | {self.email}."
            )

            user_id, user_uuid, user_country, login_id = self.get_promo_details()
            self.extract_promo_key(user_id, user_uuid, user_country, login_id)
            key = self.get_promo_key()

            Logger.info(
                f"[{thread_id}] Successfully created promo code | {key}."
            )

            thread_lock.acquire()
            with open("promos.txt", "a") as f:
                f.write(
                    f"https://promos.discord.gg/{key}"
                )
            thread_lock.release()

        except Exception as e:
            if "NoKeysLeftInPoolError" in str(e):
                end_gen = True

            Logger.error(
                f"[{thread_id}] {str(e)}"
            )


if __name__ == "__main__":

    def create_promo(thread_id):
        Logger.info(
            f"[{thread_id}] Started task."
        )
        GeneratePromo().generate_promo(thread_id)

    thread_amount = int(input(Logger.inp("Thread Amount: ")))
    print()

    while not end_gen:
        threads = []
        for i in range(thread_amount):
            t = threading.Thread(target=create_promo, args=(i + 1, ))
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    else:
        print()
        Logger.error(
            "Ended creator due to no stock of promo keys."
        )
