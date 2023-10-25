import requests
import argparse
import json
import enum
import logging
import sys
import time

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

IRQ_TX_DONE_MASK = 0x08
IRQ_RX_DONE_MASK = 0x40

class Rfm98BaseReg(enum.Enum):
    FIFO = 0x0
    OP_MODE = 0x1
    FREQ_MSB = 0x06
    FREQ_MID = 0x07
    FREQ_LSB = 0x08
    PA_POWER_CONFIG = 0x09
    PA_RAMP_TIME = 0x0a
    OVER_CURRENT_PROTECTION = 0x0b
    LNA_SET = 0x0c
    DIO_MAPPING_1 = 0x40
    DIO_MAPPING_2 = 0x41
    VERSION = 0x42
    TCXO = 0x4b
    PA_DAC = 0x4d
    FORMER_TEMPERATURE = 0x5b
    AGC_REF = 0x61
    AGC_THREASH1 = 0x62
    AGC_THREASH2 = 0x63
    AGC_THREASH3 = 0x64

class Rfm98LoraReg(enum.Enum):
    FIFO_ADDR_PTR = 0x0d
    FIFO_TX_BASE_ADDR = 0x0e
    FIFO_RX_BASE_ADDR = 0x0f
    FIFO_RX_CURRENT_ADDR = 0x10
    IRQ_FLAGS_MASK = 0x11
    IRQ_FLAGS = 0x12
    NUM_RX_BYTES = 0x13
    RX_HEADER_CNT_VALUE_MSB = 0x14
    RX_HEADER_CNT_VALUE_LSB = 0x15
    RX_PACKET_CNT_VALUE_MSB = 0x16
    RX_PACKET_CNT_VALUE_LSB = 0x17
    MODEM_STATUS = 0x18
    PACKET_SNR_VALUE = 0x19
    PACKET_RSSI_VALUE = 0x1a
    RSSI_VALUE = 0x1b
    HOP_CHANNEL = 0x1c
    MODULATION_CFG1 = 0x1d
    MODULATION_CFG2 = 0x1e
    SYMB_TIMEOUT_LSB = 0x1f
    PREAMBLE_MSB = 0x20
    PREAMBLE_LSB = 0x21
    PAYLOAD_LENGTH = 0x22
    MAX_PAYLOAD_LENGTH = 0x23
    HOP_PERIOD = 0x24
    FIFO_RX_BYTE_ADDR = 0x25
    MODULATION_CFG3 = 0x26

class LoraRfm98:
    def __init__(self, ip, mosi_pin):
        self.platform_ip = ip
        self.mosi_pin = mosi_pin
        self.spi_mode = 0
        self.spi_speed = 1000   # 1000kHz = 1mHz SPI clock
        if self.mosi_pin > 7:
            self.miso_pin = mosi_pin - 1
            self.sck_pin = mosi_pin - 2
            self.cs_pin = mosi_pin - 3
        else:
            self.miso_pin = mosi_pin + 1
            self.sck_pin = mosi_pin + 2
            self.cs_pin = mosi_pin + 3
    
    def _get_opmode(self):
        opmode = self._register_read(Rfm98BaseReg.OP_MODE)[0]
        print(f"opmode: {opmode}")
    
    def _get_frequency(self):
        regs = self._register_read(Rfm98BaseReg.FREQ_MSB, 3)
        freq = (((regs[0] << 16) + (regs[1] << 8) + (regs[0])) * (32000000)) >> 19
        return freq
    
    def _set_frequency(self, freq):
        msb = (int(((freq << 19) / 32000000)) >> 16) & 0xFF
        mid = (int(((freq << 19) / 32000000)) >> 8) & 0xFF
        lsb = int(((freq << 19) / 32000000)) & 0xFF
        self._register_write(Rfm98BaseReg.FREQ_MSB, msb)
        self._register_write(Rfm98BaseReg.FREQ_MID, mid)
        self._register_write(Rfm98BaseReg.FREQ_LSB, lsb)

    def _set_power(self):
        # Default value PA_HF/LF or +17dBm
        self._register_write(Rfm98BaseReg.PA_DAC, 0x84)
        self._register_write(Rfm98BaseReg.OVER_CURRENT_PROTECTION, 100)
        self._register_write(Rfm98BaseReg.PA_POWER_CONFIG, 0x8F)
    
    def _set_explicit_header(self):
        module_cfg_1 = self._register_read(Rfm98LoraReg.MODULATION_CFG1)[0]
        self._register_write(Rfm98LoraReg.MODULATION_CFG1, module_cfg_1 & 0xfe)

    def _register_read(self, reg, read_len = 1):
        url = f"http://{self.platform_ip}/hardware/operation"
        reg_val = reg.value & 0x7f
        request_data = {
            "event": "now",
            "actions": [["spi", 0, self.mosi_pin, self.miso_pin, self.sck_pin, self.cs_pin, self.spi_speed, self.spi_mode, read_len, 1, reg_val]]
        }
        r = requests.post(url, data=json.dumps(request_data)).json()
        return r["result"][0]

    def _register_write(self, reg, data):
        url = f"http://{self.platform_ip}/hardware/operation"
        reg_val = reg.value | 0b10000000
        if hasattr(data, '__len__'):
            request_data = {
                "event": "now",
                "actions": [["spi", 0, self.mosi_pin, self.miso_pin, self.sck_pin, self.cs_pin, self.spi_speed, self.spi_mode, 0, len(data) + 1, reg_val]]
            }
            request_data["actions"][0].extend(data)
        else:
            request_data = {
                "event": "now",
                "actions": [["spi", 0, self.mosi_pin, self.miso_pin, self.sck_pin, self.cs_pin, self.spi_speed, self.spi_mode, 0, 2, reg_val, data]]
            }
        r1 = requests.post(url, data=json.dumps(request_data))
        r = r1.json()
        if r["result"][0][0] != 'succeeded':
            logger.error(f"register write failed. Req: {request_data}, Resp: {r}")
            sys.exit(1)
    
    def _start_packet(self):
        self._set_explicit_header()
        self._register_write(Rfm98LoraReg.FIFO_ADDR_PTR, 0)
        self._register_write(Rfm98LoraReg.PAYLOAD_LENGTH, 0)

    def _transmit_data(self, data):
        current_payload_len = self._register_read(Rfm98LoraReg.PAYLOAD_LENGTH)[0]
        logger.info(f"current payload len: {current_payload_len}")
        self._register_write(Rfm98BaseReg.FIFO, data)
        self._register_write(Rfm98LoraReg.PAYLOAD_LENGTH, current_payload_len + len(data))

    def _end_packet(self):
        self._register_write(Rfm98BaseReg.OP_MODE, 0b10000011)
        while True:
            irq = self._register_read(Rfm98LoraReg.IRQ_FLAGS)[0]
            if irq & IRQ_TX_DONE_MASK != 0:
                break
        self._register_write(Rfm98LoraReg.IRQ_FLAGS, IRQ_TX_DONE_MASK)

    def begin(self):
        resp = self._register_read(Rfm98BaseReg.VERSION)[0]
        if resp != 0x12:
            logger.error(f"Version register is wrong: {resp}")
            sys.exit(1)
        self._register_write(Rfm98BaseReg.OP_MODE, 0b10000000)
        resp = self._register_read(Rfm98BaseReg.OP_MODE)[0]
        self._set_frequency(433000000)
        freq = self._get_frequency()
        logger.info(f"frequency: {freq}")
        self._register_write(Rfm98LoraReg.FIFO_TX_BASE_ADDR, 0)
        self._register_write(Rfm98LoraReg.FIFO_RX_BASE_ADDR, 0)
        lna = self._register_read(Rfm98BaseReg.LNA_SET)[0] | 0x03
        self._register_write(Rfm98BaseReg.LNA_SET, lna)
        self._register_write(Rfm98LoraReg.MODULATION_CFG3, 0x04)
        self._set_power()
        self._register_write(Rfm98BaseReg.OP_MODE, 0b10000001)

    def _has_pending_packet(self):
        has_pending = False
        irq = self._register_read(Rfm98LoraReg.IRQ_FLAGS)[0]
        if irq & IRQ_RX_DONE_MASK != 0:
            has_pending = True
        if irq != 0:
            self._register_write(Rfm98LoraReg.IRQ_FLAGS, irq)
        if has_pending:
            packet_len = self._register_read(Rfm98LoraReg.NUM_RX_BYTES)[0]
        else:
            packet_len = 0
        return packet_len

    def _read_packet(self, packet_len):
        if packet_len > 0:
            rcv_data = bytearray(self._register_read(Rfm98BaseReg.FIFO, packet_len))
            return rcv_data.decode()
        return None

    def transmit(self, data):
        self._start_packet()
        self._transmit_data(data)
        self._end_packet()

    def receive(self, timeout=10):
        self._set_explicit_header()
        end_time_second = time.time() + timeout
        while True:
            mode = self._register_read(Rfm98BaseReg.OP_MODE)[0]
            if mode != 0b10000101:
                self._register_write(Rfm98LoraReg.FIFO_ADDR_PTR, 0)
                self._register_write(Rfm98BaseReg.OP_MODE, 0b10000101)  # LONG_RANGE_MODE | RX_SINGLE
            packet_len = self._has_pending_packet()
            if packet_len > 0:
                read_data = self._read_packet(packet_len)
                logger.info(f"received: {read_data}")
            current_second = time.time()
            if current_second > end_time_second:
                break

    def dump_all_regs(self):
        r = self._register_read(Rfm98BaseReg.VERSION)
        print(f"{Rfm98BaseReg.VERSION}:{r}")

def main(args):
    lora_rfm98 = LoraRfm98(args.ip, args.mosi_pin)
    lora_rfm98.begin()
    if args.receiver:
        lora_rfm98.receive(20)
    else:
        lora_rfm98.transmit("hello".encode())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            f"Lora RFM98 module test script"
        )
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--receiver", action="store_true", help="set RFM98 as receiver")
    group.add_argument("--transmitter", action="store_true", help="set RFM98 as transimitter")
    parser.add_argument("--ip", type=str, help="ip address of the platform", required=True)
    parser.add_argument("--mosi-pin", type=int, help="pin number of spi mosi", default=0)
    args = parser.parse_args()
    main(args)
    