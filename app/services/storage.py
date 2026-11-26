import asyncio
import io
import uuid
from pathlib import Path
from urllib.parse import urlparse

from fastapi import UploadFile
from PIL import Image

from app.settings import settings

MAX_SIDE = settings.image_max_side
ALLOWED = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


class StorageService:
    def __init__(self, media_root: str | None = None, media_url: str | None = None):
        self.media_root = Path(media_root or settings.media_root)
        self.media_url = (media_url or settings.media_url).rstrip("/")

    def _resize(self, raw: bytes) -> bytes:
        img = Image.open(io.BytesIO(raw))
        img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        out = io.BytesIO()
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img.save(out, format="JPEG", quality=85)
        return out.getvalue()

    async def upload(self, file: UploadFile) -> str:
        if file.content_type not in ALLOWED:
            raise ValueError(f"unsupported content type: {file.content_type}")
        raw = await file.read()
        data = await asyncio.to_thread(self._resize, raw)
        name = f"{uuid.uuid4().hex}.jpg"
        path = self.media_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_bytes, data)
        return f"{self.media_url}/{name}"

    async def delete_by_url(self, url: str | None) -> None:
        if not url:
            return
        name = Path(urlparse(url).path).name
        path = self.media_root / name
        await asyncio.to_thread(path.unlink, True)

    async def copy_upload_file(self, file: UploadFile) -> UploadFile:
        """
        Роутер вызывает copy_upload_file(image), ожидая объект UploadFile
        Поскольку file.read() в upload() поток, копируем содержимое
        в новый UploadFile, чтобы оригинал не был сломан
        """
        raw = await file.read()
        return UploadFile(
            file=io.BytesIO(raw),
            filename=file.filename,
            headers=file.headers,
        )

    async def process_upload_file(self, file: UploadFile, *, collection_group: bool = False) -> str:
        return await self.upload(file)
