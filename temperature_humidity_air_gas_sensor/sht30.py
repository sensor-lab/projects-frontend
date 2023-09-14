#!/usr/bin/python3

import time
import requests
import argparse
import pathlib
import json
import os
import sys
from datetime import datetime
from pytz import timezone

# user requires to redefine the following 3 variables
SDA_PIN = 0
SCL_PIN = 1
ADDR_PIN = 16
PLATFORM_IP = "192.168.1.120"


def setup_address():
    url = f"http://{PLATFORM_IP}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["gpio", ADDR_PIN, "output", 0]]
    }
    requests.post(url, data=json.dumps(request_data)).json()


def start_single_shot():
    url = f"http://{PLATFORM_IP}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["i2c", 0, "write", SDA_PIN, SCL_PIN, 100, 68, 36, 11, 0]]
    }
    r = requests.post(url, data=json.dumps(request_data)).json()
    if r["result"][0][0] != 0:
        print("single shot command failed!")
        raise


def read_single_shot_result():
    url = f"http://{PLATFORM_IP}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["i2c", 0, "read", SDA_PIN, SCL_PIN, 100, 68, -1, -1, 6]]
    }
    r = requests.post(url, data=json.dumps(request_data)).json()
    temperature = -45.0 + 175.0 * \
        (((r["result"][0][0] << 8) + r["result"][0][1]) / 65535)
    humidity = 100.0 * (((r["result"][0][3] << 8) + r["result"][0][4]) / 65535)
    return temperature, humidity


def main(args):
    #setup_address()
    if args.file_name != None:
        # empty file
        open(str(args.file_name) + "_temperature", "w")
        open(str(args.file_name) + "_humidity", "w")
        while True:
            start_single_shot()
            time.sleep(0.5)
            temp, humidity = read_single_shot_result()
            pacific_tz = timezone("US/Pacific")
            time_str = datetime.now(
                tz=pacific_tz).strftime("%m/%d/%Y %H:%M:%S")
            temp_log = f"{time_str} : {temp}\r\n"
            humidity_log = f"{time_str} : {humidity}\r\n"
            with open(str(args.file_name) + "_temperature", "a") as f:
                f.write(temp_log)
            with open(str(args.file_name) + "_humidity", "a") as f:
                f.write(humidity_log)
            time.sleep(args.interval)

    else:
        start_single_shot()
        time.sleep(0.5)
        temp, humidty = read_single_shot_result()
        print(f"temperature: {temp} C, humidity: % {humidty}")


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
