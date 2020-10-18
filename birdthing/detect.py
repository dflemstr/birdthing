from multiprocessing import Value, Array, Condition
from os import path
from typing import Sequence

import numpy
import tensorflow
from tflite_runtime import interpreter

from birdthing import camera
from birdthing.label import create_category_index_from_labelmap
from birdthing.visualization import (
    visualize_boxes_and_labels_on_image_array,
    draw_keypoints_on_image_array,
)

DATA_DIR = path.join(path.dirname(__file__), "data")
LABEL_MAP = create_category_index_from_labelmap(
    path.join(DATA_DIR, "mscoco_label_map.pbtxt"), use_display_name=True
)
RESOLUTION = (320, 320)
FOV_ANGLE = 30.0


def create_detect_input_array() -> Array:
    return Array("B", RESOLUTION[0] * RESOLUTION[1] * 3)


def create_preview_array() -> Array:
    return Array("B", camera.RESOLUTION[0] * camera.RESOLUTION[1] * 3)


def label_to_category_index(labels: Sequence[str]):
    return tuple(
        map(
            lambda x: x["id"], filter(lambda x: x["name"] in labels, LABEL_MAP.values())
        )
    )


def run(
    detect_input: Array,
    new_detect_input: Condition,
    frame: Array,
    preview: Array,
    new_preview: Condition,
    target_offset_x: Value,
    target_offset_y: Value,
    track: Sequence[str],
    target_in_sight: Condition,
):
    interp = interpreter.Interpreter(
        model_path=path.abspath(
            path.join(
                DATA_DIR, "model_postprocessed_quantized_128_uint8_edgetpu.tflite"
            )
        ),
        experimental_delegates=[
            tensorflow.lite.experimental.load_delegate("libedgetpu.so.1")
        ],
    )

    interp.allocate_tensors()
    input_details = interp.get_input_details()
    output_details = interp.get_output_details()
    label_idxs = label_to_category_index(track)

    while True:
        with new_detect_input:
            new_detect_input.wait()

        with detect_input.get_lock():
            input = numpy.asarray(detect_input.get_obj()).reshape(
                (RESOLUTION[1], RESOLUTION[0], 3)
            )
            input_tensor = tensorflow.convert_to_tensor(input, dtype=tensorflow.uint8)
            input_tensor = input_tensor[tensorflow.newaxis, ...]

            interp.set_tensor(input_details[0]["index"], input_tensor)

        interp.invoke()
        box_data = tensorflow.convert_to_tensor(
            interp.get_tensor(output_details[0]["index"])
        )
        class_data = tensorflow.convert_to_tensor(
            interp.get_tensor(output_details[1]["index"])
        )
        score_data = tensorflow.convert_to_tensor(
            interp.get_tensor(output_details[2]["index"])
        )
        # num_detections = tensorflow.convert_to_tensor(
        #    interp.get_tensor(output_details[3]["index"])
        # )

        class_data = (
            tensorflow.squeeze(class_data, axis=[0]).numpy().astype(numpy.int64) + 1
        )
        box_data = tensorflow.squeeze(box_data, axis=[0]).numpy()
        score_data = tensorflow.squeeze(score_data, axis=[0]).numpy()

        if any(item in label_idxs for item in class_data):
            tracked = ((i, x) for i, x in enumerate(class_data) if x in label_idxs)
            tracked_idxs, tracked_classes = zip(*tracked)

            if any(score_data[i] > 0.6 for i in tracked_idxs):
                with target_in_sight:
                    target_in_sight.notify_all()

            idx = max(
                tracked_idxs,
                key=lambda i: numpy.amax(box_data[i]) - numpy.amin(box_data[i]),
            )

            keypoint_x = numpy.take(box_data[idx], [1, 3]).mean()
            keypoint_y = numpy.take(box_data[idx], [0, 2]).mean()

            target_offset_x.value = (keypoint_x - 0.5) * FOV_ANGLE
            target_offset_y.value = (keypoint_y - 0.5) * FOV_ANGLE
        else:
            keypoint_x = None
            keypoint_y = None

            target_offset_x.value = float("nan")
            target_offset_y.value = float("nan")

        with preview.get_lock():
            preview_image = numpy.frombuffer(
                preview.get_obj(), dtype=numpy.uint8
            ).reshape((camera.RESOLUTION[1], camera.RESOLUTION[0], 3))
            with frame.get_lock():
                frame_image = numpy.frombuffer(
                    frame.get_obj(), dtype=numpy.uint8
                ).reshape((camera.RESOLUTION[1], camera.RESOLUTION[0], 3))
                numpy.copyto(preview_image, frame_image)

            if keypoint_x is not None and keypoint_y is not None:
                draw_keypoints_on_image_array(
                    preview_image,
                    numpy.array([[keypoint_y, keypoint_x]]),
                    use_normalized_coordinates=True,
                )

            visualize_boxes_and_labels_on_image_array(
                preview_image,
                box_data,
                class_data,
                score_data,
                LABEL_MAP,
                use_normalized_coordinates=True,
                line_thickness=4,
                min_score_thresh=0.5,
                max_boxes_to_draw=3,
            )
        with new_preview:
            new_preview.notify_all()
