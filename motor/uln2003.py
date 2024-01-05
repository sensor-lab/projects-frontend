import requests
import argparse
import json
import logging
import math

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

STRIDE_ANGLE = 5.625
PHASE_DELAY = 5  # millisec
DEFAULT_ROTATION_SPEED = 5  # RPM
NUM_FULL_STEP_REVOLUTION = 2048
NUM_HALF_STEP_REVOLUTION = NUM_FULL_STEP_REVOLUTION * 2
DELAY_MS_MINIMUM = 1
DELAY_MS_MAXMIMUM = 200


class Uln2003StepperMotor:
    def __init__(self, ip, in1_pin):
        self.platform_ip = ip
        if in1_pin > 7:
            self.in1_pin = in1_pin
            self.in2_pin = in1_pin - 1
            self.in3_pin = in1_pin - 2
            self.in4_pin = in1_pin - 3
        else:
            self.in1_pin = in1_pin
            self.in2_pin = in1_pin + 1
            self.in3_pin = in1_pin + 2
            self.in4_pin = in1_pin + 3
        self._reset_io()

    def _reset_io(self):
        url = f"http://{self.platform_ip}/hardware/operation"
        request_data = {
            "event": "now",
            "actions": [
                ["gpio", self.in1_pin, "output", 0],
                ["gpio", self.in2_pin, "output", 0],
                ["gpio", self.in3_pin, "output", 0],
                ["gpio", self.in4_pin, "output", 0],
            ],
        }
        r = requests.post(url, data=json.dumps(request_data)).json()
        logger.info(f"reset IN: {r}")

    def _calculate_delay(self, rpm, full_step):
        """
        Convert from RPM to delay in ms
        """
        if full_step:
            delay = (60 * 1000) / rpm / NUM_FULL_STEP_REVOLUTION  # convert to ms
        else:
            delay = (60 * 1000) / rpm / NUM_HALF_STEP_REVOLUTION
        if delay < DELAY_MS_MINIMUM:
            logger.warning(f"RPM is set too high, use the maximum speed")
            delay = DELAY_MS_MINIMUM
        elif delay > DELAY_MS_MAXMIMUM:
            logger.warning(f"RPM is set too low, use the minimum speed")
            delay = DELAY_MS_MINIMUM
        else:
            delay = int(delay)
        logger.info(f"Each step delay: {delay}ms")
        return delay

    def _rotate_strides(self, delay, full_step, reverse):
        if reverse:
            phase1_pin = self.in4_pin
            phase2_pin = self.in3_pin
            phase3_pin = self.in2_pin
            phase4_pin = self.in1_pin
        else:
            phase1_pin = self.in1_pin
            phase2_pin = self.in2_pin
            phase3_pin = self.in3_pin
            phase4_pin = self.in4_pin

        if full_step:
            # for full-step 32 steps for 5.625 degree
            cycle = [
                ["gpio", phase1_pin, "output", 1],
                ["gpio", phase4_pin, "output", 0],
                ["delay", 0, "ms", delay],
                ["gpio", phase2_pin, "output", 1],
                ["gpio", phase1_pin, "output", 0],
                ["delay", 0, "ms", delay],
                ["gpio", phase3_pin, "output", 1],
                ["gpio", phase2_pin, "output", 0],
                ["delay", 0, "ms", delay],
                ["gpio", phase4_pin, "output", 1],
                ["gpio", phase3_pin, "output", 0],
                ["delay", 0, "ms", delay],
            ]
        else:
            # for half-step 64 steps for 5.625 degree
            cycle = [
                ["gpio", phase1_pin, "output", 1],
                ["gpio", phase4_pin, "output", 0],
                ["delay", 0, "ms", delay],
                ["gpio", phase1_pin, "output", 1],
                ["gpio", phase2_pin, "output", 1],
                ["delay", 0, "ms", delay],
                ["gpio", phase2_pin, "output", 1],
                ["gpio", phase1_pin, "output", 0],
                ["delay", 0, "ms", delay],
                ["gpio", phase2_pin, "output", 1],
                ["gpio", phase3_pin, "output", 1],
                ["delay", 0, "ms", delay],
                ["gpio", phase3_pin, "output", 1],
                ["gpio", phase2_pin, "output", 0],
                ["delay", 0, "ms", delay],
                ["gpio", phase3_pin, "output", 1],
                ["gpio", phase4_pin, "output", 1],
                ["delay", 0, "ms", delay],
                ["gpio", phase4_pin, "output", 1],
                ["gpio", phase3_pin, "output", 0],
                ["delay", 0, "ms", delay],
                ["gpio", phase4_pin, "output", 1],
                ["gpio", phase1_pin, "output", 1],
                ["delay", 0, "ms", delay],
            ]
        actions = []
        for i in range(0, 8):
            actions.extend(cycle)
        url = f"http://{self.platform_ip}/hardware/operation"
        request_data = {"event": "now", "actions": actions}
        logger.info(f"request: {request_data}")
        r = requests.post(url, data=json.dumps(request_data)).json()
        logger.info(f"response: {r}")

    def rotate_angle(self, angle, speed, full_step, reverse=False):
        delay = self._calculate_delay(speed, full_step)
        num_of_stride = math.ceil(angle / STRIDE_ANGLE)
        for i in range(0, num_of_stride):
            self._rotate_strides(delay, full_step, reverse)

    def rotate_revolution(self, num_revolution, speed, full_step, reverse):
        self.rotate_angle(num_revolution * 360, speed, full_step, reverse)


def main(args):
    motor = Uln2003StepperMotor(args.ip, args.pin)
    if args.angle == None:
        # rotate with revolution
        motor.rotate_revolution(
            args.revolution, args.speed, args.full_step, args.reverse
        )
    else:
        # rotate with angle
        motor.rotate_angle(args.angle, args.speed, args.full_step, args.reverse)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(f"ULN2003 stepper motor driver script")
    )
    parser.add_argument(
        "--ip", type=str, help="ip address of the platform", required=True
    )
    parser.add_argument(
        "--pin", type=int, help="pin id connected to the IN1 on ULN2003", required=True
    )
    parser.add_argument(
        "--speed",
        type=float,
        help="rotation speed in RPM",
        default=DEFAULT_ROTATION_SPEED,
    )
    parser.add_argument(
        "--reverse",
        default=False,
        action="store_true",
        help="motor rotates reverse direction",
    )
    parser.add_argument(
        "--full-step",
        default=False,
        action="store_true",
        help="use full stepping mode, default is half stepping for better stability",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--angle", type=int, help="rotate motor by angle")
    group.add_argument("--revolution", type=float, help="rotate motor by revolution")
    args = parser.parse_args()
    main(args)
