import time
from math import isnan
from multiprocessing import Value

from adafruit_servokit import ServoKit

MAX_PULSE = 2500
MIN_PULSE = 500
ACTUATION_RANGE = 300
MIN_PAN_ANGLE = 105
MAX_PAN_ANGLE = 120
INITIAL_PAN_ANGLE = MIN_PAN_ANGLE  # (MIN_PAN_ANGLE + MAX_PAN_ANGLE) // 2
MIN_TILT_ANGLE = 174
MAX_TILT_ANGLE = 190
INITIAL_TILT_ANGLE = MIN_TILT_ANGLE  # (MIN_TILT_ANGLE + MAX_TILT_ANGLE) // 2
SLEEP = 0.01


def run(target_offset_x: Value, target_offset_y: Value):
    kit = ServoKit(channels=16, frequency=100)

    pan_servo = kit.servo[0]
    pan_servo.actuation_range = ACTUATION_RANGE
    pan_servo.set_pulse_width_range(MIN_PULSE, MAX_PULSE)

    tilt_servo = kit.servo[1]
    tilt_servo.actuation_range = ACTUATION_RANGE
    tilt_servo.set_pulse_width_range(MIN_PULSE, MAX_PULSE)

    pan_servo.angle = INITIAL_PAN_ANGLE
    tilt_servo.angle = INITIAL_TILT_ANGLE

    while True:
        time.sleep(SLEEP)
        offset_x = target_offset_x.value
        if not isnan(offset_x):
            target_offset_x.value = float("nan")
            pan_servo.angle = clamp(
                pan_servo.angle + offset_x * 0.1, MIN_PAN_ANGLE, MAX_PAN_ANGLE
            )

        offset_y = target_offset_y.value
        if not isnan(offset_y):
            target_offset_y.value = float("nan")
            tilt_servo.angle = clamp(
                tilt_servo.angle - offset_y * 0.1, MIN_TILT_ANGLE, MAX_TILT_ANGLE
            )


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)
