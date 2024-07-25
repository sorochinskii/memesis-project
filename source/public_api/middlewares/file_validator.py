from fastapi import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from settings import settings

routes = [
    '/v1/memes/'
]


class ValidateUploadFileMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_upload_size: int = settings.MAX_IMAGE_SIZE) -> None:
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request,
                       call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in routes and request.method == 'POST':
            if 'content-length' not in request.headers:
                return Response(status_code=status.HTTP_411_LENGTH_REQUIRED)
            content_length = int(request.headers['content-length'])
            if content_length > self.max_upload_size:
                return Response(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        return await call_next(request)
