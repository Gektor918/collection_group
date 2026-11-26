from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from db.models.models import CollectionGroup, CollectionGroupTranslation


@dataclass(slots=True, frozen=True)
class CollectionGroupTranslationDTO:
    id: int
    relation_id: int
    company_id: int | None
    lang: str
    name: str | None
    description: str | None

    @classmethod
    def from_model(
        cls, m: "CollectionGroupTranslation"
    ) -> "CollectionGroupTranslationDTO":
        return cls(
            id=m.id,
            relation_id=m.relation_id,
            company_id=m.company_id,
            lang=m.lang,
            name=m.name,
            description=m.description,
        )

    def as_dict_translation(self) -> dict[str, Any]:
        return {"lang": self.lang, "name": self.name}


@dataclass(slots=True)
class CollectionGroupDTO:
    id: int
    company_id: int | None
    image: str | None
    order: int | None
    disable: bool
    archived: bool | None = None
    translations: list[CollectionGroupTranslationDTO] = field(default_factory=list)

    @classmethod
    def from_model(
        cls,
        m: "CollectionGroup",
        *,
        translations: Iterable["CollectionGroupTranslation"] | None = None,
    ) -> "CollectionGroupDTO":
        if translations is None:
            loaded = m.__dict__.get("translations")
            translations = loaded if loaded is not None else ()

        return cls(
            id=m.id,
            company_id=m.company_id,
            image=m.image,
            order=m.order,
            disable=bool(m.disable),
            archived=m.archived,
            translations=[CollectionGroupTranslationDTO.from_model(t) for t in translations],
        )

    def translation(self, lang: str) -> CollectionGroupTranslationDTO | None:
        for t in self.translations:
            if t.lang == lang:
                return t
        return None

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "image": self.image,
            "disable": self.disable,
            "order": self.order,
        }

    def as_full_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "company_id": self.company_id,
            "image": self.image,
            "order": self.order,
            "disable": self.disable,
            "archived": self.archived,
            "translations": [t.as_dict_translation() for t in self.translations],
        }


@dataclass(slots=True, frozen=True)
class CollectionRealmDTO:

    id: int
    group_id: int | None
    company_id: int | None
    order: int | None

    @classmethod
    def from_model(cls, m) -> "CollectionRealmDTO":
        return cls(id=m.id, group_id=m.group_id, company_id=m.company_id, order=m.order)


@dataclass(slots=True, frozen=True)
class CollectionGroupUpdateResult:
    dto: CollectionGroupDTO
    old_image: str | None


@dataclass(slots=True, frozen=True)
class CollectionGroupDeleteResult:
    group_id: int
    old_image: str | None
