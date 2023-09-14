#!/usr/bin/python3

# datasheet: https://datasheet.lcsc.com/lcsc/2205131645_Aosong--Guangzhou-Elec-AGS02MA_C3012633.pdf

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


def single_read_air_pollute_val():
    url = f"http://{PLATFORM_IP}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["i2c", 0, "write", SDA_PIN, SCL_PIN, 10, 26, 0, -1, 0], ["i2c", 0, "read", SDA_PIN, SCL_PIN, 10, 26, -1, -1, 5]]
    }
    r = requests.post(url, data=json.dumps(request_data)).json()
    air_pollute_val = (r["result"][1][0] << 24) + (r["result"][1][1] << 16) + (r["result"][1][2] << 8) + (r["result"][1][3])
    return air_pollute_val

def main(args):
    if args.file_name != None:
        # empty file
        open(args.file_name, "w")
        while True:
            air_pollute_val = single_read_air_pollute_val()
            pacific_tz = timezone("US/Pacific")
            time_str = datetime.now(
                tz=pacific_tz).strftime("%m/%d/%Y %H:%M:%S")
            air_pollute_log = f"{time_str} : {air_pollute_val}\r\n"
            with open(args.file_name, "a") as f:
                f.write(air_pollute_log)
            time.sleep(args.interval)

    else:
        air_pollute_val = single_read_air_pollute_val()
        print(f"air pollute val: {air_pollute_val}")
        if air_pollute_val < 300:
            print("空气质量：优/良")
        elif air_pollute_val < 1500:
            print("空气质量：微量污染")
        elif air_pollute_val < 3000:
            print("空气质量：轻度污染")
        elif air_pollute_val < 5000:
            print("空气质量：中度污染")
        elif air_pollute_val < 10000:
            print("空气质量：重度污染")
        else:
            print("空气质量：未知")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            f"Record air pollute value of ags02ma sensor"
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
