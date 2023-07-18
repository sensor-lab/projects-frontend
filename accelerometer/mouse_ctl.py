# ADXL345 accelerometer control

import pyautogui
import requests
import json
import time

SENSOR_LAB_IP_ADDR = "192.168.1.101"

def enable_accelerometer(address=SENSOR_LAB_IP_ADDR):
    url = 'http://{}/hardware/operation'.format(address)
    request_data ={
        "event":"now",
        "actions": [["i2c", 0, "write", 0, 1, 400, 83, 45,-1, 1,8]]
    }
    requests.post(url, data=json.dumps(request_data))

def get_accelerometer_readings(address=SENSOR_LAB_IP_ADDR):
    url = 'http://{}/hardware/operation'.format(address)
    request_data = {
        "event":"now",
        "actions": [["i2c", 0, "write", 0, 1, 400, 83, 50,-1, 0],["i2c", 0, "read", 0, 1, 400, 83, -1,-1, 6],["i2c", 0, "write", 0, 1, 400, 83, 57,-1, 0],["i2c", 0, "read", 0, 1, 400, 83, -1,-1, 1]]
    }
    r = requests.post(url, data=json.dumps(request_data)).json()
    x_axis = r["result"][1][0] + (r["result"][1][1] << 8)
    y_axis = r["result"][1][2] + (r["result"][1][3] << 8)
    z_axis = r["result"][1][4] + (r["result"][1][5] << 8)
    if x_axis >= 0x8000:
        x_axis -= 0x10000
    if y_axis >= 0x8000:
        y_axis -= 0x10000
    if z_axis >= 0x8000:
        z_axis -= 0x10000

    return (x_axis, y_axis, z_axis)

def setup_single_tap(address=SENSOR_LAB_IP_ADDR):
    url = 'http://{}/hardware/operation'.format(address)
    request_data ={
        "event":"now",
        "actions": [["i2c", 0, "write", 0, 1, 400, 83, 29,-1, 1,48],["i2c", 0, "write", 0, 1, 400, 83, 33,-1, 1,16],["i2c", 0, "write", 0, 1, 400, 83, 34,-1, 1,64]]
    }
    reply = requests.post(url, data=json.dumps(request_data))
    print(f"reply1 : {reply.json()}")

    request_data ={
        "event":"now",
        "actions": [["i2c", 0, "write", 0, 1, 400, 83, 56,-1, 1,64],["i2c", 0, "write", 0, 1, 400, 83, 39,-1, 1,16],["i2c", 0, "write", 20, 1, 400, 83, 46,-1, 1,64]]
    }
    reply = requests.post(url, data=json.dumps(request_data))
    print(f"reply2: {reply.json()}")

    request_data ={
        "event":"now",
        "actions": [["i2c", 0, "write", 20, 21, 400, 83, 42,-1, 1,1],["i2c", 0, "write", 20, 21, 400, 83, 39,-1, 1,16],["i2c", 0, "write", 20, 21, 400, 83, 46,-1, 1,64]]
    }
    reply = requests.post(url, data=json.dumps(request_data))
    print(f"reply3: {reply.json()}")


def main():
    clicked = False
    # setup_single_tap()
    enable_accelerometer()
    while True:
        x_pos, y_pos = pyautogui.position()
        x_axis, y_axis, z_axis = get_accelerometer_readings()
        if x_axis > 200:
            x_pos += 75
        elif x_axis > 150:
            x_pos += 50
        elif x_axis > 100:
            x_pos += 10
        elif x_axis > 50:
            x_pos += 5
        elif x_axis < -200:
            x_pos -= 75
        elif x_axis < -150:
            x_pos -= 50
        elif x_axis < -100:
            x_pos -= 10
        elif x_axis < -50:
            x_pos -= 5

        if y_axis > 200:
            y_pos += 75
        elif y_axis > 150:
            y_pos += 50
        elif y_axis > 100:
            y_pos += 10
        elif y_axis > 50:
            y_pos += 5
        elif y_axis < -200:
            y_pos -= 75
        elif y_axis < -150:
            y_pos -= 50
        elif y_axis < -100:
            y_pos -= 10
        elif y_axis < -50:
            y_pos -= 5

        # print(f"z: {z_axis}, time: {time.time()}")
        pyautogui.moveTo(x_pos, y_pos, duration = 0.001)

        if clicked == True and (z_axis > 400 or z_axis < 100):
            pyautogui.rightClick()
            clicked = False
        elif z_axis > 400 or z_axis < 100:
            clicked = True
        elif clicked:
            pyautogui.leftClick()
            clicked = False

        print(f"x: {x_axis}, y: {y_axis}, z: {z_axis}  time: {time.time()}")

if __name__ == "__main__":
    main()