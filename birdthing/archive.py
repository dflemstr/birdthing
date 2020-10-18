import logging
from datetime import datetime
from multiprocessing import Condition, Array
from pathlib import Path

from PIL import Image

from birdthing import camera


def run(frame: Array, target_in_sight: Condition):
    archive_path = Path("/mnt/nas/data/birdthings")
    archive_path.mkdir(exist_ok=True, parents=True)
    while True:
        with target_in_sight:
            target_in_sight.wait()

        with frame.get_lock():
            now = datetime.now()
            if not (7 < now.hour < 18):
                continue
            datepart, timepart = str(now).split(" ")
            dest = (
                archive_path / datepart / timepart.split(":")[0] / (timepart + ".jpeg")
            )
            dest.parent.mkdir(exist_ok=True, parents=True)
            Image.frombytes("RGB", camera.RESOLUTION, frame.get_obj()).save(
                dest, format="jpeg"
            )
            logging.info(f'archived image {dest}')
