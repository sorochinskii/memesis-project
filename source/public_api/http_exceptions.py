from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from logger_config import logger

HTTPUnknownUploadStatus = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail='Not uploaded'
)

HTTPStorageIsNotAvailable = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Storage not available'
)

HTTPPrivatePostFailed = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail='Resource not created'
)

HTTPUnsupportedFileType = HTTPException(
    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    detail='Unsupported media type'
)

HTTPUnsupportedContentSize = HTTPException(
    status_code=status.HTTP_411_LENGTH_REQUIRED,
    detail='Unsupported file length'
)

HTTPUnsupportedFileSize = HTTPException(
    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    detail='File too large'
)

HTTPUploadFileError = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail='File problem'
)

HTTPObjectNotExist = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Item not found'
)

HTTPTokenExpiredError = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Signature has expired'
)

HTTPJWTDecodeError = HTTPException(
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    detail='JWT decode error.'
)
