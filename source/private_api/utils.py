from settings import settings


def s3_file_path(filename: str) -> str:
    path = f'{settings.S3_SERVICE_NAME}://' + \
        f'{settings.S3_USER}:' + \
        f'{settings.S3_PASSWORD}@' + \
        f'{settings.S3_HTTP_HOST}:' + \
        f'{settings.S3_HTTP_PORT}@' + \
        f'{settings.S3_BUCKET}/' + \
        f'{filename}'
    return path
