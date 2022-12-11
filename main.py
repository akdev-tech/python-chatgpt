import httpx
import logging
import argparse

import config
from auth import Auth
from stream import Stream

parser = argparse.ArgumentParser(description="ChatGPT dialog without browser")
parser.add_argument(
    "-u",
    "--username",
    dest="username",
    help="Your username (email) for openai.com",
    required=True,
)
parser.add_argument(
    "-p",
    "--password",
    dest="password",
    help="Your password for openai.com",
    required=True,
)
parser.add_argument(
    "-m",
    "--message",
    dest="message",
    help="Message for ChatGPT",
    required=True,
)
parser.add_argument(
    "-vvv",
    "--verbose",
    action="store_true",
    dest="verbose",
    help="Enable debug logging level",
)

args = parser.parse_args()


level = (logging.DEBUG if args.verbose else logging.INFO)
logging.basicConfig(level=level)


def log_request(req):
    logging.debug(f"Request event hook: {req.method} {req.url}")


def log_response(resp):
    req = resp.request
    logging.debug(f"Response event hook: {req.method} {req.url}")
    logging.debug(f"Status - {resp.status_code}")
    logging.debug(resp.read())
    for cookie in resp.cookies:
        logging.debug("Cookie", cookie, resp.cookies[cookie])
    for header in resp.headers:
        logging.debug("Header", header, resp.headers[header])


if args.verbose:
    event_hooks = {"request": [log_request], "response": [log_response]}
else:
    event_hooks = None

session = httpx.Client(
    http2=True,
    headers=config.initial_headers,
    event_hooks=event_hooks,
    follow_redirects=True,
    cookies=Auth.load_cookies(httpx.Cookies()),
)
session.cookies.jar.clear_expired_cookies()

while not Auth.check_auth(session):
    logging.info("Start the loging process")
    auth_instance = Auth(args.username, args.password)
    auth_instance.perform_login(session)


stream = Stream(session)
response = stream.send_message(args.message)
print(response)
