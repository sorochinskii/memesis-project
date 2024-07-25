from fastapi import Form
from pydantic import BaseModel
from starlette.responses import StreamingResponse


class FileUploadSchema(BaseModel):
    ...
    file: str = Form(...)
    # file: StreamingResponse(content_type='multipart/form')
