#!/usr/bin/python3
# TMP102 reference curl command:
# read config register
# curl --location --request POST "192.168.1.124/hardware/operation" --header 'Content-Type: application/json' --data-raw '{
#     "event":"now",
#     "actions": [["i2c", 0, "write", 20, 21, 50, 72, 1, -1, 0],["i2c", 0, "read", 20, 21, 50, 72, -1, -1, 2]]
# }'

# single-shot trigger
# curl --location --request POST "192.168.1.124/hardware/operation" --header 'Content-Type: application/json' --data-raw '{
#     "event":"now",
#     "actions": [["i2c", 0, "write", 20, 21, 50, 72, 1, -1, 2, 224, 160]]
# }'

# read temperature
# curl --location --request POST "192.168.1.124/hardware/operation" --header 'Content-Type: application/json' --data-raw '{
#     "event":"now",
#     "actions": [["i2c", 0, "write", 20, 21, 50, 72, 0, -1, 0],["i2c", 0, "read", 20, 21, 50, 72, -1, -1, 2]]
# }'


import time
import requests
import argparse
import pathlib
import json
import sys
from datetime import datetime
from pytz import timezone

# user requires to redefine the following 3 variables
SDA_PIN = 11
SCL_PIN = 10
PLATFORM_IP = "192.168.4.1"


def read_temp():
    url = f"http://{PLATFORM_IP}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["i2c", 0, "write", SDA_PIN, SCL_PIN, 50, 72, 0, -1, 0], ["i2c", 0, "read", SDA_PIN, SCL_PIN, 50, 72, -1, -1, 2]]
    }
    r = requests.post(url, data=json.dumps(request_data)).json()
    temp_val = ((r["result"][1][0] << 8) + r["result"][1][1]) >> 4
    if temp_val & (1 << 11) != 0:
        # 2's complementary
        temp_val = temp_val - (1 << 12)
    return temp_val * 0.0625


def main(args):
    if args.file_name != None:
        # empty file
        open(args.file_name, "w")
        while True:
            temp = read_temp()
            pacific_tz = timezone("US/Pacific")
            time_str = datetime.now(
                tz=pacific_tz).strftime("%m/%d/%Y %H:%M:%S")
            temp_log = f"{time_str} : {temp}\r\n"
            with open(args.file_name, "a") as f:
                f.write(temp_log)
            time.sleep(args.interval)

    else:
        temp = read_temp()
        print(f"temperature: {temp} C")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            f"Record temperature of TMP102 sensor"
        )
    )
    parser.add_argument(
        "--file-name", "-f", type=pathlib.Path, default=None, help="Saving temperature to the file"
    )
    parser.add_argument(
        "--interval", "-i", type=int, default=10, help="Time interval to read temperature in second"
    )
    args = parser.parse_args()
    main(args)
