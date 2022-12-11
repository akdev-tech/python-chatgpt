import os
import base64
import pickle
import logging
from bs4 import BeautifulSoup


class Auth:
    CAPTCHA_FILENAME = "captcha.svg"
    COOKIES_FILENAME = "cookies.pk"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @classmethod
    def get_token(cls, session):
        req = session.get("https://chat.openai.com/api/auth/session")
        return req.json().get("accessToken")

    @classmethod
    def save_cookies(cls, session):
        with open(cls.COOKIES_FILENAME, "wb") as f:
            pickle.dump(session.cookies.jar._cookies, f)

    @classmethod
    def load_cookies(cls, cookies):
        if not os.path.isfile(cls.COOKIES_FILENAME):
            return None
        with open(cls.COOKIES_FILENAME, "rb") as f:
            jar_cookies = pickle.load(f)
        for domain, pc in jar_cookies.items():
            for path, c in pc.items():
                for k, v in c.items():
                    cookies.set(k, v.value, domain=domain, path=path)
        return cookies

    @classmethod
    def check_auth(cls, session):
        token = cls.get_token(session)
        return token

    def _get_state(self, resp):
        return resp.find("input", {"name": "state", "type": "hidden"}).get("value")

    def _captcha_handler(self, resp):
        captcha = resp.find("img", {"alt": "captcha"})
        if captcha:
            src = captcha.get("src").split(",")[1]
            with open(self.CAPTCHA_FILENAME, "wb") as fh:
                fh.write(base64.urlsafe_b64decode(src))
            logging.info("Please enter captcha code: ")
            code = input()
            if os.path.isfile(self.CAPTCHA_FILENAME):
                os.remove(self.CAPTCHA_FILENAME)
            return code

    def _block_handler(self, resp):
        s = "We have detected a potential security issue with this account"
        return s in str(resp)

    def perform_login(self, session):
        req = session.get("https://chat.openai.com/api/auth/csrf")
        csrf = req.json().get("csrfToken")

        session.headers.update({"content-type": "application/x-www-form-urlencoded"})
        params = {
            "callbackUrl": "/",
            "csrfToken": csrf,
            "json": "true"
        }
        req = session.post(
            "https://chat.openai.com/api/auth/signin/auth0?prompt=login", data=params
        )
        login_link = req.json().get("url")

        req = session.get(login_link)
        response = BeautifulSoup(req.text, features="html.parser")

        while True:  # try to auth
            state = self._get_state(response)
            code = self._captcha_handler(response)

            session.headers.update({
                "content-type": "application/x-www-form-urlencoded"
            })
            params = {
                "state": state,
                "username": self.username,
                "captcha": code,
                "js-available": "true",
                "webauthn-available": "true",
                "is-brave": "false",
                "webauthn-platform-available": "false",
                "action": "default"
            }
            url = f"https://auth0.openai.com/u/login/identifier?state={state}"
            req = session.post(url, data=params)
            response = BeautifulSoup(req.text, features="html.parser")

            # break if password field is found on page
            if response.find("input", {"name": "password", "id": "password"}):
                break
            logging.info("Incorrect captcha or another error, trying again...")

        state = self._get_state(response)

        is_blocked = self._block_handler(response)

        if is_blocked:
            logging.warning("We are blocked")
            return

        req = session.get(f"https://auth0.openai.com/u/login/password?state={state}")
        response = BeautifulSoup(req.text, features="html.parser")
        state = self._get_state(response)

        session.headers.update({
            "content-type": "application/x-www-form-urlencoded"
        })
        params = {
            "state": state,
            "username": self.username,
            "password": self.password,
            "action": "default"
        }
        url = f"https://auth0.openai.com/u/login/password?state={state}"
        req = session.post(url, data=params)
        return req.url == "https://chat.openai.com/chat"
