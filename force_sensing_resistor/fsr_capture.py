import threading
import socket
import requests
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import json
import logging
import sys
import argparse
from threading import Semaphore

HOST_PORT_NUM = 5000
RCV_BUFFER_SIZE = 1440
RETURN_TYPE = "udp"     # the platform only supports UDP as return type for now.
DEFAULT_SAMPLE_RATE = 4000
DEFAULT_CAPTURE_DURATION = 5

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

adc_semaphore = Semaphore(1)
adc_capture_lst = []

class AdcDataFetchThread(threading.Thread):
    def __init__(self, platform_ip, pin, sample_rate, duration_sec, return_type, ax):
        threading.Thread.__init__(self)
        self.platform_ip = platform_ip
        self.pin = pin
        self.return_type = return_type
        self.sample_rate = sample_rate
        self.duration_sec = duration_sec
        self.ax = ax
        self.ax.set_title(f"Force sensing resistor real time plot")

        if return_type == "tcp":
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serversocket.bind((self._get_host_ip(), HOST_PORT_NUM))
            self.serversocket.listen(10)
        elif return_type == "udp":
            self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serversocket.bind((self._get_host_ip(), HOST_PORT_NUM))
            self.serversocket.settimeout(5.0)
        else:
            logger.error(f"Does not support return type {return_type}")
            sys.exit(1)

    def _get_host_ip(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            sock.connect(("10.255.255.255", 1))
            ip_addr = sock.getsockname()[0]
        except Exception:
            ip_addr = "127.0.0.1"
        finally:
            sock.close()
        return ip_addr

    def run(self):
        logger.info(f"Start adc capture")
        payload_obj = {
            "event": "now",
            "actions": [
                [
                    "adc",
                    self.pin,
                    "3.1v",
                    self.sample_rate,
                    self.duration_sec,
                    self.return_type,
                    f"{self._get_host_ip()}:{HOST_PORT_NUM}",
                ]
            ],
        }
        ret = requests.post(
            f"http://{self.platform_ip}/hardware/operation", json=payload_obj
        )
        if json.loads(ret.content)["result"][0][0] != "succeeded":
            logger.error(f"Set adc continuous failed !")
            sys.exit(1)

        if self.return_type == "tcp":
            connection, address = self.serversocket.accept()
            logger.info(f"accepted new connection {connection} from {address}")
            rcv_data = connection.recv(RCV_BUFFER_SIZE).decode("UTF-8")
        else:
            rcv_data = self.serversocket.recv(RCV_BUFFER_SIZE).decode("UTF-8")
        
        if len(rcv_data) > 0:
            adc_info = json.loads(rcv_data)[0]
            self.ax.set_ylabel(f"{adc_info} reading")

        while len(rcv_data) > 0:
            left_bound = rcv_data.find("[")
            right_bound = rcv_data.find("]")

            if left_bound != -1 and right_bound != -1:
                json_string = rcv_data[left_bound : right_bound + 1]
                try:
                    rcv_json = json.loads(json_string)
                except json.decoder.JSONDecodeError as e:
                    logger.error(f"json decode error, {rcv_data}")
                    break
                adc_semaphore.acquire()
                adc_capture_lst.extend(rcv_json[1:])
                adc_semaphore.release()
                rcv_data = rcv_data[right_bound + 1 :]
            elif left_bound != -1:
                # need have more data to form json
                pass
            else:
                logger.error(
                    f"Cannot find left bound [ sign in the payload: {rcv_data}"
                )
                rcv_data = ""
           
            try:
                if self.return_type == "tcp":
                    rcv_data += connection.recv(RCV_BUFFER_SIZE).decode("UTF-8")
                else:
                    rcv_data += self.serversocket.recv(RCV_BUFFER_SIZE).decode("UTF-8")
            except TimeoutError:
                logger.info(f"udp socket timeout, close connection")
                rcv_data = ""
            except UnicodeDecodeError:
                logger.info(f"unicode decode error, packet corrupt")
                rcv_data = "[\"adc\"]"  # give an empty payload
        if self.return_type == "tcp":
            connection.close()
        else:
            self.serversocket.close()

class ForceSensingResistorCapture:
    def __init__(self, platform_ip, connected_pin, capture_duration, sample_rate):
        frame_update_interval_ms = 50
        self.total_num_frames = int(capture_duration * (1000 / frame_update_interval_ms))
        ping_response = os.system("ping -n 1 " + platform_ip)
        if ping_response != 0:
            logger.error(f"ping platform ip {platform_ip} is failed ! Please make sure type the right ip address")
            sys.exit(1)
        logger.info(f"Force sensing resistor is connected to {connected_pin}, adc sample rate: {sample_rate}, capture duration: {capture_duration}s")
        self.t, fig, self.line, ax = self.setup_plot(capture_duration, sample_rate)
        self.animation = FuncAnimation(
            fig=fig,
            func=self.update,
            frames=self.total_num_frames,
            interval=frame_update_interval_ms,
            repeat=False,
        )
        self.adc_capture_thread = AdcDataFetchThread(platform_ip, connected_pin, sample_rate, capture_duration, RETURN_TYPE, ax)
    
    def update(self, frame):
        adc_semaphore.acquire()
        self.line.set_xdata(self.t[0 : len(adc_capture_lst)])
        self.line.set_ydata(adc_capture_lst)
        adc_semaphore.release()
        if frame == self.total_num_frames - 2:
            self.annot_max(self.t[0 : len(adc_capture_lst)], adc_capture_lst)
        return self.line

    def annot_max(self, x,y, ax=None):
        xmax = x[np.argmax(y)]
        ymax = max(y)
        text= "x={:.3f}, y={:.3f}".format(xmax, ymax)
        if not ax:
            ax=plt.gca()
        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        arrowprops=dict(arrowstyle="->",connectionstyle="angle,angleA=0,angleB=60")
        kw = dict(xycoords='data',textcoords="axes fraction",
                arrowprops=arrowprops, bbox=bbox_props, ha="right", va="top")
        ax.annotate(text, xy=(xmax, ymax), xytext=(0.94,0.96), **kw)

    def setup_plot(self, duration_sec, sample_rate):
        fig, ax = plt.subplots()
        t = np.linspace(0, duration_sec, sample_rate * duration_sec)
        line = ax.plot(t[0], 0)[0]
        ax.set(
            xlim=[0, duration_sec], ylim=[0, 4096], xlabel="Time [s]", ylabel="FSR value"
        )
        ax.legend()
        return t, fig, line, ax

    def start(self):
        self.adc_capture_thread.start()
        plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=(
            f"Cature force sensing resistor reading and generate a plot"
        )
    )
    parser.add_argument("--ip", type=str, help="ip address of the platform", required=True)
    parser.add_argument("--pin", type=int, help="pin number which connects to the fsr", default=0)
    parser.add_argument("--duration", type=int, help="how long does capture persist", default=DEFAULT_CAPTURE_DURATION)
    parser.add_argument("--sample-rate", type=int, help="adc sample rate", default=DEFAULT_SAMPLE_RATE)
    args = parser.parse_args()
    force_sensing_resistor = ForceSensingResistorCapture(args.ip, args.pin, args.duration, args.sample_rate)
    force_sensing_resistor.start()
