
import time
import requests
import argparse
import pathlib
import json
from datetime import datetime
from pytz import timezone

# user requires to redefine the following 3 variables
HALL_OUTPUT1_PIN = 11
HALL_OUTPUT2_PIN = 10
PLATFORM_IP = "192.168.1.129"


def read_hall_value():
    # single read temperature
    # send command convertT (0xCC44) then read 3 bytes out
    url = f"http://{PLATFORM_IP}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["gpio", 19, "input", 0], ["gpio", 18, "input", 0]]
    }
    r = requests.post(url, data=json.dumps(request_data)).json()
    hall_zero_val = r["result"][0][0]
    hall_one_val = r["result"][1][0]
    # temperature equation can be found in the data sheet
    return hall_zero_val, hall_one_val


def main(args):
    while True:
        pacific_tz = timezone("US/Pacific")
        time_str = datetime.now(
            tz=pacific_tz).strftime("%m/%d/%Y %H:%M:%S.%f")
        hall_zero, hall_one = read_hall_value()
        print(f"time: {time_str} hall zero: {hall_zero}, hall one: {hall_one}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            f"Reading hall effect sensor"
        )
    )
    args = parser.parse_args()
    main(args)
