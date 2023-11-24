import requests
import sys
import json
import time
import argparse
import datetime
from enum import Enum

PLATFORM_IP = "192.168.1.106"
ULTRASONIC_PIN = 0
LED_STRIP_PIN = 4
MAX_PAYLOAD_LEN = 8000
NUMBER_LEDS = 26
ULTRASONIC_CAPTURE_NUMBER_LOOPS = 15
ULTRASONIC_THRESHOLD_MIDDLE = 14000
ULTRASONIC_THRESHOLD_CLOSE = 3000
STABLE_COUNT_VAL = 2        # 2 consecutive

class LedState(Enum):
    LED_OFF = 1
    LED_RED = 2
    LED_BLINK = 3

def read_ultrasonic(platform_ip, echo_pin_id, trigger_pin_id):
    url = f"http://{platform_ip}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["capture", echo_pin_id, 10, "us", "change", 0.1, "trigger", trigger_pin_id, "high", "us", 10]]
    }
    result = requests.post(url, data=json.dumps(request_data)).json()["result"]
    print(f"time: {datetime.datetime.now()} echo length: {result[0][2]}")
    return result[0][2]

def led_strip_setup(platform_ip, led_pin_id):
    url = f"http://{platform_ip}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["advance_output", led_pin_id,"setup","us","zero", 2.5,0.5, "one",2.5,1.2]]
    }
    result = requests.post(url, data=json.dumps(request_data)).json()["result"]
    if result[0][0] != "succeeded":
        print(f"led setup failed: {result[0]}")
        sys.exit(1)

def led_strip_color(platform_ip, led_pin_id, num_led, red, green, blue):
    url = f"http://{platform_ip}/hardware/operation"
    request_data = {
        "event": "now",
        "actions": [["advance_output", led_pin_id, "start", num_led * 3]]
    }
    colors = []
    for i in range(0, num_led):
        colors.append(green)
        colors.append(red)
        colors.append(blue)
      
    request_data["actions"][0].extend(colors)
    result = requests.post(url, data=json.dumps(request_data)).json()["result"]



LED_COLOR_SCHEMA = [
    [20, 0, 0],
    [0, 10, 0],
    [0, 0, 10],
    [0, 10, 10],
    [10, 10, 0],
    [10, 0, 10],
    [20, 0, 10],
    [20, 10, 0],
    [0, 20, 10],
    [10, 10, 10],
    [10, 20, 0],
    [0, 20, 0],
    [10, 0, 20],
    [0, 0, 20],
    [20, 20, 20],
    [5, 5, 5],
]

def main(ip, ultrasonic_pin, led_pin):
    led_state = False
    far_stable_counter = 0
    middle_stable_counter = 0
    close_stable_counter = 0

    led_strip_setup(ip, led_pin)
    while True:
        echo_us = read_ultrasonic(ip, ultrasonic_pin, ultrasonic_pin)

        if echo_us > ULTRASONIC_THRESHOLD_MIDDLE:
            far_stable_counter += 1
            if far_stable_counter >= STABLE_COUNT_VAL:
                middle_stable_counter = 0
                close_stable_counter = 0
                if led_state != LedState.LED_OFF:
                    led_strip_color(ip, led_pin, NUMBER_LEDS, 0, 0, 0)
                    time.sleep(0.5)
                    led_state = LedState.LED_OFF
        elif echo_us > ULTRASONIC_THRESHOLD_CLOSE:
            middle_stable_counter += 1
            if middle_stable_counter >= STABLE_COUNT_VAL:
                far_stable_counter = 0
                close_stable_counter = 0
                if led_state != LedState.LED_RED:
                    led_strip_color(ip, led_pin, NUMBER_LEDS, 30, 0, 0)
                    time.sleep(0.5)
                    led_state = LedState.LED_RED
        else:
            close_stable_counter += 1
            if close_stable_counter >= STABLE_COUNT_VAL:
                far_stable_counter = 0
                middle_stable_counter = 0
                led_strip_color(ip, led_pin, NUMBER_LEDS, 0, 20, 0)
                time.sleep(0.4)
                led_strip_color(ip, led_pin, NUMBER_LEDS, 20, 20, 0)
                time.sleep(0.4)
                led_state = LedState.LED_BLINK




if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=(
            f"Use ultrasonic to measure distance and shine the LED strip for different distance"
        )
    )
    parser.add_argument("--ip", type=str, help="ip address of the platform", required=True)
    parser.add_argument("--ultrasonic-pin", type=int, help="pin which connects to the ultrasonic module", default=0)
    parser.add_argument("--led-pin", type=int, help="pin which connects to the WS2812 led strip", default=4)
    args = parser.parse_args()
    force_sensing_resistor = main(args.ip, args.ultrasonic_pin, args.led_pin)
