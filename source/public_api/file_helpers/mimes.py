from enum import Enum


class ImageTypes(str, Enum):
    jpeg = 'image/jpeg'
    jpg = 'image/jpeg'
    png = 'image/png'

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
