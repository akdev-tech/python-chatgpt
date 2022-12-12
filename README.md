# ChatGPT without browser with pure Python

**UPDATE 12.12.2022**

Now ChatGPT has Cloudflare protection.

No Selenium or another testing tools. Pure Python.

Now performs login, handles captcha, sends message and prints ChatGPT answer.

Disclaimer: just for dev purposes.

## Getting Started

Create the account for ChatGPT (login by email and password).

### Installing

```
$ git clone https://github.com/akdev-tech/python-chatgpt.git
$ cd python-chatgpt
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```


### Running

```
$ python3 main.py -u <email> -p <password> -m "<message>"
```

If it asks for captcha code, you can take a captcha image at `captcha.svg`. The captcha code is case sensitive!

To run in `debug` mode add the `-vvv` flag.

## Known issues

* Occasional uncatched errors


## Future plans

1. Make a module package
2. Automatic solving captchas
3. Consider ChatGPT rate-limits 
4. Type annotations
