from multiprocessing import Condition, Array

import picamera
import picamera.array
import numpy

RESOLUTION = (2048, 1536)
FRAMERATE = 30


def create_frame_array() -> Array:
    return Array("B", RESOLUTION[0] * RESOLUTION[1] * 3)


def run(frame: Array, new_frame: Condition):
    with picamera.PiCamera(resolution=RESOLUTION) as camera, picamera.array.PiRGBArray(
        camera, size=RESOLUTION
    ) as data_container:
        stream = camera.capture_continuous(
            data_container, format="rgb", use_video_port=True
        )

        f: picamera.array.PiArrayOutput
        for f in stream:
            with frame.get_lock():
                image = numpy.frombuffer(frame.get_obj(), dtype=numpy.uint8).reshape(
                    (RESOLUTION[1], RESOLUTION[0], 3)
                )
                numpy.copyto(image, f.array)

            with new_frame:
                new_frame.notify_all()

            data_container.seek(0)
            data_container.truncate()
