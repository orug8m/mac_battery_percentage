import os
import psutil
import requests
import logging

import json
import time
import hashlib
import hmac
import base64
import uuid

TOKEN = os.environ["SWITCH_BOT_TOKEN"]
SECRET = bytes(os.environ["SWITCH_BOT_SECRET"], 'utf-8')
PLUG_MINI_LETS_BUILD_DEVICE_ID = os.environ["PLUG_MINI_LETS_BUILD_DEVICE_ID"]
PLUG_MINI_TALK_TO_ME_DEVICE_ID = os.environ["PLUG_MINI_TALK_TO_ME_DEVICE_ID"]

API_HOST = 'https://api.switch-bot.com'
DEBIVELIST_URL = f"{API_HOST}/v1.1/devices"
t = str(int(round(time.time() * 1000)))
nonce = uuid.uuid4()
string_to_sign = '{}{}{}'.format(TOKEN, t, nonce)
string_to_sign = bytes(string_to_sign, 'utf-8')
sign = base64.b64encode(hmac.new(SECRET, msg=string_to_sign, digestmod=hashlib.sha256).digest())

HEADERS = {
    'Authorization': TOKEN,
    'Content-Type': 'application/json; charset=utf8',
    'charset': 'utf8',
    't': str(t),
    'sign': str(sign, 'utf-8'),
    'nonce': str(nonce),
}

def logger():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, encoding='utf-8',filename='./log/development.log')
    return logger


def _get_request(url):
    res = requests.get(url, headers=HEADERS)
    data = res.json()
    if data['message'] == 'success':
        return res.json()
    return {}


def _post_request(url, params):
    res = requests.post(url, data=json.dumps(params), headers=HEADERS)
    data = res.json()
    if data['message'] == 'success':
        return res.json()
    return {}


def get_device_list():
    try:
        return _get_request(DEBIVELIST_URL)["body"]
    except:
        return


# def get_virtual_device_list():
#     devices = get_device_list()
#     return devices

def get_device_status(device_id):
    try:
        return _get_request(f"{DEBIVELIST_URL}/{device_id}/status")["body"]
    except:
        return

# Plug Mini commands: {"command": "turnOn"}, {"command": "turnOff"}, {"command": "toggle"}
def post_device_control_commands(device_id, params):
    try:
        return _post_request(f"{DEBIVELIST_URL}/{device_id}/commands", params)["body"]
    except:
        return

# percent: int
def main(percent):
    device_list = get_device_list()
    # print(device_list)

    # for device in device_list['deviceList']:
    #     device_status = get_device_status(device['deviceId'])
    #     print(device_status)

    device_status = get_device_status(PLUG_MINI_LETS_BUILD_DEVICE_ID)
    print(device_status)
    power = device_status['power']

    power_on = power == 'on'
    power_off = power == 'off'
    enough = percent > 80
    shortage = percent < 20

    print("Power ON: ", power_on)
    print("Power OFF:", power_off)
    print("Percent Enough: ", enough)
    print("Percent Shortage: ", shortage)

    if shortage and power_off:
        params = {"command": "turnON"}
        print(params)
        logger.info("{}, {}".format(percent,'off'))
        post_device_control_commands(PLUG_MINI_LETS_BUILD_DEVICE_ID, params)
    elif enough and power_on:
        params = {"command": "turnOFF"}
        print(params)
        logger.info("{}, {}".format(percent,'on'))
        post_device_control_commands(PLUG_MINI_LETS_BUILD_DEVICE_ID, params)
    logger.info("{}, {}".format(percent,'keep'))


if __name__ == "__main__":
    battery = psutil.sensors_battery()
    percent = battery.percent
    logger = logger()

    print("Battery: ", percent, '%')
    main(percent)
