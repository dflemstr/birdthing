from multiprocessing.dummy import Array, Condition
import PIL.Image as Image
import numpy


def run(
    input_image: Array,
    new_input_image: Condition,
    input_size: (int, int),
    output_image: Array,
    new_output_image: Condition,
    output_size: (int, int),
):
    while True:
        with new_input_image:
            new_input_image.wait()

        with input_image.get_lock():
            image = Image.frombuffer("RGB", input_size, input_image.get_obj())
            result = image.resize(output_size, resample=Image.NEAREST)

        with output_image.get_lock():
            dest = numpy.frombuffer(output_image.get_obj(), dtype=numpy.uint8).reshape(
                (output_size[0], output_size[1], 3)
            )
            numpy.copyto(dest, numpy.array(result))

        with new_output_image:
            new_output_image.notify_all()


def crop_resize(image, size, ratio):
    # crop to ratio, center
    w, h = image.size
    if w > ratio * h:  # width is larger then necessary
        x, y = (w - ratio * h) // 2, 0
    else:  # ratio*height >= width (height is larger)
        x, y = 0, (h - w / ratio) // 2
    image = image.crop((x, y, w - x, h - y))

    # resize
    if image.size > size:  # don't stretch smaller images
        image.thumbnail(size, Image.NEAREST)
    return image
