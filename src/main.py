import argparse
import base64
import hashlib
import hmac
import json
import os
import time
import uuid

import psutil
import requests
from retry import retry

from logger import Logger

TOKEN = os.environ["SWITCH_BOT_TOKEN"]
SECRET = bytes(os.environ["SWITCH_BOT_SECRET"], "utf-8")
PLUG_MINI_LETS_BUILD_DEVICE_ID = os.environ["PLUG_MINI_LETS_BUILD_DEVICE_ID"]
PLUG_MINI_TALK_TO_ME_DEVICE_ID = os.environ["PLUG_MINI_TALK_TO_ME_DEVICE_ID"]

API_HOST = "https://api.switch-bot.com"
DEBIVELIST_URL = f"{API_HOST}/v1.1/devices"
t = str(int(round(time.time() * 1000)))
nonce = uuid.uuid4()
string_to_sign = "{}{}{}".format(TOKEN, t, nonce)
string_to_sign = bytes(string_to_sign, "utf-8")
sign = base64.b64encode(
    hmac.new(SECRET, msg=string_to_sign, digestmod=hashlib.sha256).digest()
)

HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json; charset=utf8",
    "charset": "utf8",
    "t": str(t),
    "sign": str(sign, "utf-8"),
    "nonce": str(nonce),
}


class RequestError(Exception):
    pass


class SwitchBot:
    def __init__(self, force_on, force_off):
        self.force_on = force_on
        self.force_off = force_off
        self.logger = Logger()

    @retry(RequestError, tries=3, delay=1)
    def _get_request(self, url):
        res = requests.get(url, headers=HEADERS)
        data = res.json()

        if data["message"] == "success":
            return data
        else:
            self.logger.error(data)
            raise RequestError("Failed to get request")

    @retry(RequestError, tries=3, delay=1)
    def _post_request(self, url, params):
        res = requests.post(url, data=json.dumps(params), headers=HEADERS)
        data = res.json()

        if data["message"] == "success":
            return data
        else:
            self.logger.error(data)
            raise RequestError("Failed to post request")

    def get_device_list(self):
        try:
            return self._get_request(DEBIVELIST_URL)["body"]
        except RequestError:
            return

    # def get_virtual_device_list():
    #     devices = get_device_list()
    #     return devices

    def get_device_status(self, device_id):
        try:
            return self._get_request(f"{DEBIVELIST_URL}/{device_id}/status")["body"]
        except RequestError:
            return

    # Plug Mini commands: {"command": "turnOn"}, {"command": "turnOff"}, {"command": "toggle"}
    def post_device_control_commands(self, device_id, params):
        try:
            res = self._post_request(f"{DEBIVELIST_URL}/{device_id}/commands", params)
            return res["body"]
        except RequestError:
            return

    def post_toggle_status(self, params, device_id):
        post_param = {**params, **{"parameter": "default", "commandType": "command"}}
        return self.post_device_control_commands(device_id, post_param)

    def fetch_mac_battery_percentile(self):
        battery = psutil.sensors_battery()
        return battery.percent

    def main(self):
        device_status = self.get_device_status(PLUG_MINI_LETS_BUILD_DEVICE_ID)
        power = device_status["power"]
        percent = self.fetch_mac_battery_percentile()

        enough = percent > 80
        shortage = percent < 20
        power_on = power == "on"

        if (shortage and not power_on) or self.force_on:
            self.logger.info("{}, {}".format(percent, "turn on"))
            self.post_toggle_status(
                {"command": "turnOn"}, PLUG_MINI_LETS_BUILD_DEVICE_ID
            )
        elif (enough and power_on) or self.force_off:
            self.logger.info("{}, {}".format(percent, "turn off"))
            self.post_toggle_status(
                {"command": "turnOff"}, PLUG_MINI_LETS_BUILD_DEVICE_ID
            )
        else:
            self.logger.info("{}, {}".format(percent, "keep"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force_on", action="store_true")
    parser.add_argument("--force_off", action="store_true")

    force_on = parser.parse_args().force_on
    force_off = parser.parse_args().force_off

    switch_bot = SwitchBot(force_on, force_off)
    print("Battery: ", switch_bot.fetch_mac_battery_percentile(), "%")
    switch_bot.main()
