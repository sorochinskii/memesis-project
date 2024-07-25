from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import BaseCommon, IDUUIDMixin, created_at, updated_at


class Memes(BaseCommon, IDUUIDMixin):
    name: Mapped[str] = mapped_column()
    text: Mapped[str | None] = mapped_column()
    extension: Mapped[str] = mapped_column()
    delete_mark: Mapped[bool | None] = mapped_column(default=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    media_type: Mapped[str | None] = mapped_column(default=None)
