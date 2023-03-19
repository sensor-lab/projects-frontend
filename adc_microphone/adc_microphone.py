#!/usr/bin/env python3
import wave, json, socket, requests, asyncore, logging, os
from enum import Enum
from scipy.fft import rfft, rfftfreq
import matplotlib.pyplot as plt
import matplotlib.font_manager as mfm
import numpy as np

RECTCREAM_IP_ADDRESS = '192.168.1.102'
HOST_IP_ADDRESS = '192.168.1.114'
HOST_PORT_NUM = 5000
SAMPLE_RATE = 2000 # hertz
SAMPLE_WIDTH = 2    # 16-bit
NUM_OF_AUDIO_CHANNEL = 1
RCV_BUFFER_SIZE = 1460
ADC_FILTER_OUT_THRESHOLD=20
BACKLOG = 5

adc_samples = []

class ReturnType(Enum):
    RETURN_TCP = 0,
    RETURN_UDP = 1

class CaptureSampleHandler(asyncore.dispatcher):

    def __init__(self, sock, capture_list):
        asyncore.dispatcher.__init__(self, sock)
        self.capture_list = capture_list

    def handle_read(self):
        rcv_data = self.recv(RCV_BUFFER_SIZE)
        if len(rcv_data) > 0:
            rcv_json = json.loads(rcv_data)
            self.capture_list.extend(rcv_json[1:])

    def handle_close(self):
        asyncore.dispatcher.handle_close(self)
        asyncore.close_all()

class AdcMicrophone(asyncore.dispatcher):
    def __init__(self, host_port, offset=0):
        asyncore.dispatcher.__init__(self)
        self.host_ip = self.__get_host_ip()
        self.host_port = host_port
        self.samples = []
        self.sample_rate = 0
        self.duration = 0
        self.offset = offset
        self.create_socket()
        self.set_reuse_addr()
        self.bind((self.host_ip, self.host_port))
        self.listen(BACKLOG)
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def __get_host_ip(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            sock.connect(('10.255.255.255', 1))
            ip_addr = sock.getsockname()[0]
        except Exception:
            ip_addr = '127.0.0.1'
        finally:
            sock.close()
        return ip_addr

    def __butter_highpass(self, cutoff, fs, order=5):
        return butter(order, cutoff, fs=fs, btype='high', analog=False)

    def filter_out_noise(self, cutoff, order=5):
        b, a = self.__butter_highpass(cutoff, self.sample_rate, order=order)
        y = filtfilt(b, a, self.samples)
        return y

    def readable(self):
        return True

    def handle_accepted(self, sock, addr):
        self.logger.info(f'Incoming connection from {addr}')
        handler = CaptureSampleHandler(sock, self.samples)

    def handle_close(self):
        asyncore.dispatcher.handle_close(self)

    def capture_samples(self, sample_rate, duration, \
                        return_type: ReturnType, \
                        rectcream_ip,   \
                        adc_channel_id = 0, \
                        adc_ref_voltage = '5v'):
        self.samples.clear()
        self.sample_rate = sample_rate
        self.duration = duration
        return_type_str = 'tcp' if return_type is ReturnType.RETURN_TCP else 'udp'
        return_dest_str = f'{self.host_ip}:{self.host_port}'

        payload_obj = {
            "event": "now",
            "actions": [["adc", adc_channel_id, adc_ref_voltage, sample_rate, "s", duration, \
                        return_type_str, return_dest_str]]
        }

        ret = requests.post(f'http://{rectcream_ip}/hardware/operation', json=payload_obj)
        asyncore.loop()
        self.logger.info(f'Captured samples: {len(self.samples)}')

    def get_samples(self):
        return self.samples

    def normalize_adc_samples(self):
        for i in range(len(self.samples)):
            # sometimes ADC gives very low samples, filter them out
            temp_data = np.int16(self.samples[i] - self.offset).item() if self.samples[i] > ADC_FILTER_OUT_THRESHOLD else 0
            self.samples[i] = temp_data

    def save_wave(self, file_name='sound.wav', wave_data=None):
        wave_obj = wave.open(file_name,'w')
        wave_obj.setnchannels(NUM_OF_AUDIO_CHANNEL)
        wave_obj.setsampwidth(SAMPLE_WIDTH)
        wave_obj.setframerate(self.sample_rate)
        samples = wave_data if wave_data is not None else self.samples
        for data in samples:
            # left shift since to convert 10 bits to 16 bits
            wave_obj.writeframesraw((data << 6).to_bytes(2,'little',signed=True))
        wave_obj.close()

    def fft_transform(self):
        return rfft(self.samples), rfftfreq(len(self.samples), 1 / self.sample_rate)

if __name__ == '__main__':
    MICROPHONE_ADC_OFFSET = 250
    DURATION = 5

    adc_microphone = AdcMicrophone(HOST_PORT_NUM, MICROPHONE_ADC_OFFSET)
    adc_microphone.capture_samples(SAMPLE_RATE, DURATION, ReturnType.RETURN_TCP, '192.168.1.104')
    adc_microphone.normalize_adc_samples()
    adc_microphone.save_wave()

    font_path = os.path.join(os.getcwd(), os.path.dirname(__file__), 'AaKaiSong.ttf')
    prop = mfm.FontProperties(fname=font_path,size=10)

    # plotting
    fig, axs = plt.subplots(ncols=2)

    axs[0].set_title(u'声音信号ADC采样',fontproperties=prop)
    samples = adc_microphone.get_samples()
    timeline_x_axis = np.linspace(0, DURATION, len(samples), endpoint=False)
    axs[0].plot(timeline_x_axis, samples)
    axs[0].set_xlabel(u'时间(秒)',fontproperties=prop)
    axs[0].set_ylabel(u'ADC采样值',fontproperties=prop)

    axs[1].set_title(u'傅立叶变换',fontproperties=prop)
    freq_y_axis, freq_x_axis = adc_microphone.fft_transform()
    axs[1].plot(freq_x_axis, np.abs(freq_y_axis))
    axs[1].set_xlabel(u'频率(Hz)',fontproperties=prop)
    axs[1].set_ylabel(u'幅度',fontproperties=prop)

    plt.show()

