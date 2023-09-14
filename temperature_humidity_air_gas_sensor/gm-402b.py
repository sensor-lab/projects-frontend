#!/usr/bin/python3

# datasheet: https://datasheet.lcsc.com/lcsc/1811061516_Zhengzhou-Winsen-Elec-Tech-GM-402B_C99754.pdf

import time
import requests
import argparse
import pathlib
import json
import sys
from datetime import datetime
from pytz import timezone

# user requires to redefine the following 3 variables
ADC_PIN = 2
PLATFORM_IP = "192.168.1.120"

def single_read_gas_level():
    url = f"http://{PLATFORM_IP}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["adc", ADC_PIN, "3.1v"]]
    }
    r = requests.post(url, data=json.dumps(request_data)).json()
    print(f"adc: {r}")
    return 0

def main(args):
    if args.file_name != None:
        # empty file
        open(args.file_name, "w")
        while True:
            air_pollute_val = single_read_gas_level()
            pacific_tz = timezone("US/Pacific")
            time_str = datetime.now(
                tz=pacific_tz).strftime("%m/%d/%Y %H:%M:%S")
            air_pollute_log = f"{time_str} : {air_pollute_val}\r\n"
            with open(args.file_name, "a") as f:
                f.write(air_pollute_log)
            time.sleep(args.interval)
    else:
        air_pollute_val = single_read_gas_level()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            f"Record flammable gas level of gm-402b sensor"
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
