from fastapi import HTTPException, status

from settings import settings

HTTPUnknownUploadStatus = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail='Not uploaded.'
)

HTTPStorageIsNotAvailable = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Storage not available'
)

HTTPFileIsMissing = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail='File is missing')

HTTPFileSizeLimitException = HTTPException(
    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    detail=f'Maximum file size limit {settings.MAX_FILE_SIZE} bytes exceeded')

HTTPCommonUploadException = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail='There was an error uploading the file')

HTTPObjectNotExist = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Storage not available'
)
