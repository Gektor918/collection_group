from pydantic import BaseModel, Field
from enum import Enum as DefaultEnum


class languageEnum(str, DefaultEnum):
    en = "en"
    ru = "ru"


class CollectionGroupLocale(BaseModel):
    name: str | None = None
    description: str | None = None


class CollectionGroupCreateRequest(BaseModel):
    company_id: int
    lang: dict[languageEnum, CollectionGroupLocale]


class CollectionGroupUpdateRequest(BaseModel):
    company_id: int
    id: int
    disable: bool | None = None
    lang: dict[languageEnum, CollectionGroupLocale] | None = None


class CollectionGroupUpdateListCommon(BaseModel):
    company_id: int
    id: int
    new_collections: list[int] = []
    delete_collections: list[int] = []


class CollectionGroupLocaleItem(BaseModel):
    lang: languageEnum
    name: str | None = None
    description: str | None = None


class CollectionGroupDTO(BaseModel):
    id: int
    image: str | None = None
    order: int | None = None
    disable: bool
    locales: list[CollectionGroupLocaleItem] = []


class CollList(BaseModel):
    items: list[CollectionGroupDTO]


class CollItems(BaseModel):
    items: CollectionGroupDTO


class CollItemId(BaseModel):
    items: int


class CollOrders(BaseModel):
    items: dict[int, int]


class CollUpdateList(BaseModel):
    new_collections: list[int]
    delete_collections: list[int]


class CollectionGroupUpdateOrderRequest(BaseModel):
    company_id: int
    orders: dict[int, int] = Field(..., examples=[{"2": 1, "1": 2}])


class CollectionRealmItem(BaseModel):
    id: int
    group_id: int | None = None
    company_id: int | None = None
    order: int | None = None


class CollectionRealmList(BaseModel):
    items: list[CollectionRealmItem]
    total: int = Field(default=0, description="всего realm'ов в компании")
    assigned: int = Field(default=0, description="привязано к какой-либо группе")
    unassigned: int = Field(default=0, description="group_id IS NULL — свободны или отвязаны")
