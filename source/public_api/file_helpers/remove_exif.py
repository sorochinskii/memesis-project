from io import BytesIO

from PIL import Image


def remove_exif(file: BytesIO) -> BytesIO:
    image_file = Image.open(file)
    data = list(image_file.getdata())
    image_without_exif = Image.new(image_file.mode, image_file.size)
    image_without_exif.putdata(data)
    return image_without_exif
