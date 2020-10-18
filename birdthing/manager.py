import time
from multiprocessing import Manager, Process
from typing import Sequence

from birdthing import servos, detect, server, camera, resize, archive


def run(track: Sequence[str]):
    with Manager() as manager:
        target_offset_x = manager.Value("f", 0)
        target_offset_y = manager.Value("f", 0)

        frame = camera.create_frame_array()
        detect_input = detect.create_detect_input_array()
        preview = detect.create_preview_array()
        new_frame = manager.Condition()
        new_detect_input = manager.Condition()
        new_preview = manager.Condition()
        target_in_sight = manager.Condition()

        processes = [
            Process(
                name="camera",
                target=camera.run,
                args=(frame, new_frame),
            ),
            Process(
                name="resize",
                target=resize.run,
                args=(
                    frame,
                    new_frame,
                    camera.RESOLUTION,
                    detect_input,
                    new_detect_input,
                    detect.RESOLUTION,
                ),
            ),
            Process(
                name="detect",
                target=detect.run,
                args=(
                    detect_input,
                    new_detect_input,
                    frame,
                    preview,
                    new_preview,
                    target_offset_x,
                    target_offset_y,
                    track,
                    target_in_sight,
                ),
            ),
            Process(
                name="archive",
                target=archive.run,
                args=(
                    frame,
                    target_in_sight,
                ),
            ),
            Process(
                name="servos",
                target=servos.run,
                args=(target_offset_x, target_offset_y),
            ),
            Process(
                name="server",
                target=server.run,
                args=(
                    preview,
                    new_preview,
                    target_offset_x,
                    target_offset_y,
                    ("0.0.0.0", 8000),
                ),
            ),
        ]

        for process in processes:
            process.start()

        while all(process.is_alive() for process in processes):
            time.sleep(10)

        for process in processes:
            process.terminate()

        for process in processes:
            process.join()
