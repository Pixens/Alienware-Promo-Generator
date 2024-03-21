import os
import yaml
import time
import string
import random
import requests
if os.name == "nt":
    import ctypes

from bs4 import BeautifulSoup


with open("config.yml", "r") as c:
    config = yaml.safe_load(c)

class Data:
    generated = int()


CAPSOLVER_KEY = config["capsolver-key"]


class Utils:

    @staticmethod
    def generate_password():
        upper_case_letter = random.choice(string.ascii_uppercase)
        lower_case_string = ''.join(random.choices(string.ascii_lowercase, k=5))
        digit = random.choice(string.digits)
        special_char = random.choice(["!", "@", "#", "$", "%", "&", "*"])

        password = upper_case_letter + lower_case_string + digit + special_char
        password = list(password)
        random.shuffle(password)
        password = ''.join(password)
        return password

    @staticmethod
    def generate_username():
        # Partly taken from https://github.com/williexu/random_username/

        with open("./data/adjectives.txt", "r") as adjectives_file:
            adjectives = adjectives_file.read().splitlines()
        with open("./data/nouns.txt", "r") as nouns_file:
            nouns = nouns_file.read().splitlines()

        adjective = random.choice(adjectives)
        noun = random.choice(nouns).capitalize()
        num = str(random.randrange(10))
        username = adjective + noun + num

        return username

    @staticmethod
    def fetch_email() -> str:
        response = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
        if response.status_code == 200:
            email = response.json()[0]
            return email
        else:
            return Utils.fetch_email()

    @staticmethod
    def solve_recaptcha(user_agent: str, page_action: str) -> str:
        task_payload = {
            "clientKey": CAPSOLVER_KEY,
            "appId": "C10FB33E-8CED-4F6D-990C-356E42F5E318",
            "task": {
                "type": "ReCaptchaV3TaskProxyLess",
                "websiteURL": "https://in.alienwarearena.com/",
                "websiteKey": "6LfRnbwaAAAAAPYycaGDRhoUqR-T0HyVwVkGEnmC",
                "pageAction": page_action,
                "userAgent": user_agent
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
    def extract_token(html: str, name: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        token = soup.find('input', {'name': name}).get('value')
        return token

    @staticmethod
    def extract_link(html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        activation_link = soup.find('a', class_='mcnButton')['href']
        return activation_link

    @staticmethod
    def extract_verification_link(user: str, domain: str) -> str:
        count = int()
        while count < 60:
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
                time.sleep(3)
        else:
            raise Exception(f"Failed to get verification email | {user}@{domain}")

    @staticmethod
    def set_title():
        if os.name == "nt":
            while True:
                title = f"Alienware Promo Generator | github.com/Pixens | Generated: {Data.generated}"
                ctypes.windll.kernel32.SetConsoleTitleW(title)
                time.sleep(3)
