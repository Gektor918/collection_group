import logging
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import settings

from api_collection_groups import router as api_collection_groups
from service import CollectionGroupNotFoundError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

API_CMS = "/cms"

app = FastAPI(
    title="Collection groups slice",
    version="1.0.0",
    description="Один модуль из CMS: группы коллекций, привязки, файлы переделаны на локальные НЕ S3",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.media_root).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_root), name="media")


@app.exception_handler(CollectionGroupNotFoundError)
async def collection_group_not_found_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Collection group not found"})


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


app.include_router(api_collection_groups, prefix=API_CMS)
