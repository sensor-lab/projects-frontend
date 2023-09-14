#!/usr/bin/python3

# read status and configuration
# curl --location --request POST "192.168.1.124/hardware/operation" --header 'Content-Type: application/json' --data-raw '{
#     "event":"now",
#     "actions": [["i2c", 0, "write", 20, 21, 50, 69, 243, 45, 0],["i2c", 0, "read", 20, 21, 50, 69, -1, -1, 3]]
# }'

# single read
# curl --location --request POST "192.168.1.124/hardware/operation" --header 'Content-Type: application/json' --data-raw '{
#     "event":"now",
#     "actions": [["i2c", 0, "write", 20, 21, 50, 69, 204, 68, 0],["i2c", 0, "read", 20, 21, 50, 69, -1, -1, 3]]
# }'

# set repeat read
# curl --location --request POST "192.168.1.124/hardware/operation" --header 'Content-Type: application/json' --data-raw '{
#     "event":"now",
#     "actions": [["i2c", 0, "write", 20, 21, 50, 69, 82, 6, 3, 12, 255, 153],["i2c", 0, "write", 20, 21, 50, 69, 204, 68, 0]]
# }'

# read repeat read value
# curl --location --request POST "192.168.1.124/hardware/operation" --header 'Content-Type: application/json' --data-raw '{
#     "event":"now",
#     "actions": [["i2c", 0, "read", 20, 21, 50, 69, -1, -1, 3]]
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
SDA_PIN = 0
SCL_PIN = 1
PLATFORM_IP = "192.168.1.120"


def set_auto():
    # set auto capture in configuration register 0x5206
    # then send another convertT to start the continuing capture
    url = f"http://{PLATFORM_IP}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["i2c", 0, "write", SDA_PIN, SCL_PIN, 50, 69, 82, 6, 3, 12, 255, 153], ["i2c", 0, "write", SDA_PIN, SCL_PIN, 50, 69, 204, 68, 0]]
    }
    r = requests.post(url, data=json.dumps(request_data)).json()
    if r["result"][0][0] != 3 or r["result"][1][0] != 0:
        print("set up auto capture failed!")
        raise


def continuous_read_temp():
    url = f"http://{PLATFORM_IP}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["i2c", 0, "read", SDA_PIN, SCL_PIN, 50, 69, -1, -1, 3]]
    }
    r = requests.post(url, data=json.dumps(request_data)).json()
    temp_val = (r["result"][0][0] << 8) + r["result"][0][1]
    if temp_val & (1 << 15) != 0:
        # 2's complementary
        temp_val = temp_val - (1 << 16)
    # temperature equation can be found in the data sheet
    return 40 + (temp_val / 256)


def single_read_temp():
    # single read temperature
    # send command convertT (0xCC44) then read 3 bytes out
    url = f"http://{PLATFORM_IP}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["i2c", 0, "write", SDA_PIN, SCL_PIN, 50, 69, 204, 68, 0], ["i2c", 0, "read", SDA_PIN, SCL_PIN, 50, 69, -1, -1, 3]]
    }
    r = requests.post(url, data=json.dumps(request_data)).json()
    temp_val = (r["result"][1][0] << 8) + r["result"][1][1]
    if temp_val & (1 << 15) != 0:
        # 2's complementary
        temp_val = temp_val - (1 << 16)
    # temperature equation can be found in the data sheet
    return 40 + (temp_val / 256)


def main(args):
    if args.file_name != None:
        # empty file
        open(args.file_name, "w")
        set_auto()
        while True:
            temp = continuous_read_temp()
            pacific_tz = timezone("US/Pacific")
            time_str = datetime.now(
                tz=pacific_tz).strftime("%m/%d/%Y %H:%M:%S")
            temp_log = f"{time_str} : {temp}\r\n"
            with open(args.file_name, "a") as f:
                f.write(temp_log)
            time.sleep(args.interval)

    else:
        temp = single_read_temp()
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
