from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from services.dto import CollectionGroup, CollectionGroupTranslation

from repository import CollectionGroupRepository

from schemas import (CollectionGroupDTO, CollectionGroupLocale,
                      CollectionGroupLocaleItem, languageEnum, CollectionRealmList, CollectionRealmItem)
from common import managed_transaction


class CollectionGroupNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class GroupUpdateOut:
    dto: CollectionGroupDTO
    old_image: str | None


@dataclass(frozen=True)
class GroupDeleteOut:
    group_id: int
    old_image: str | None


class CollectionGroupService:
    def __init__(self, repo: CollectionGroupRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def list_realms(
        self,
        company_id: int,
        *,
        group_id: int | None = None,
        assigned: bool | None = None,
    ) -> CollectionRealmList:
        items = await self.repo.list_realms(
            company_id=company_id, group_id=group_id, assigned=assigned
        )
        total, assigned_count, unassigned = await self.repo.count_realms(company_id)
        return CollectionRealmList(
            items=[CollectionRealmItem(
                id=r.id,
                group_id=r.group_id,
                company_id=r.company_id,
                order=r.order,
            ) for r in items],
            total=total,
            assigned=assigned_count,
            unassigned=unassigned,
        )

    async def list_groups(
        self,
        company_id: int,
    ) -> list[CollectionGroupDTO]:
        groups = await self.repo.list_by_company(
            company_id=company_id,
        )
        return [self._to_dto(g) for g in groups]

    async def create_group(
        self,
        company_id: int,
        lang: dict[languageEnum, CollectionGroupLocale],
        image: str | None = None,
    ) -> CollectionGroupDTO:
        translations = self._build_translations(company_id, lang)
        async with managed_transaction(self.session):
            group = await self.repo.create_group(company_id, translations, image)
            return self._to_dto(group)

    async def update_group(
        self,
        group_id: int,
        company_id: int,
        lang: dict[languageEnum, CollectionGroupLocale] | None = None,
        image: str | None = None,
        disable: bool | None = None,
    ) -> GroupUpdateOut:
        async with managed_transaction(self.session):
            result = await self.repo.update_group(
                group_id=group_id,
                company_id=company_id,
                lang=lang,
                image=image,
                disable=disable,
            )
            if result is None:
                raise CollectionGroupNotFoundError()
            return GroupUpdateOut(
                dto=self._to_dto(result.group),
                old_image=result.old_image,
            )

    async def delete_group(
        self,
        group_id: int,
        company_id: int,
    ) -> GroupDeleteOut:
        async with managed_transaction(self.session):
            result = await self.repo.delete_group(group_id, company_id)
            if result is None:
                raise CollectionGroupNotFoundError()
            return GroupDeleteOut(group_id=result.group_id, old_image=result.old_image)

    async def update_group_list(
        self,
        group_id: int,
        company_id: int,
        new_collections: list[int],
        delete_collections: list[int],
    ) -> dict[str, list[int]]:
        async with managed_transaction(self.session):
            group = await self.repo.get_by_id(group_id, company_id)
            if group is None:
                raise CollectionGroupNotFoundError()

            assigned = await self.repo.assign_collections_to_group(
                group_id=group_id,
                company_id=company_id,
                collection_ids=new_collections,
            )
            unassigned = await self.repo.unassign_collections_from_group(
                group_id=group_id,
                company_id=company_id,
                collection_ids=delete_collections,
            )
            return {
                "new_collections": assigned,
                "delete_collections": unassigned,
            }

    async def update_order(
        self,
        company_id: int,
        orders: dict[int, int],
    ) -> dict[int, int]:
        if not orders:
            return {}
        async with managed_transaction(self.session):
            updated = await self.repo.update_order(company_id=company_id, orders=orders)
            if updated != orders:
                raise CollectionGroupNotFoundError()
            return updated

    @staticmethod
    def _to_dto(group: CollectionGroup) -> CollectionGroupDTO:
        locales: list[CollectionGroupLocaleItem] = []
        for t in group.translations:
            try:
                key = languageEnum(t.lang)
            except ValueError:
                continue
            locales.append(
                CollectionGroupLocaleItem(
                    lang=key,
                    name=t.name,
                    description=t.description,
                )
            )
        return CollectionGroupDTO(
            id=group.id,
            image=group.image,
            order=group.order,
            disable=group.disable,
            locales=locales,
        )

    @staticmethod
    def _build_translations(company_id: int, lang: dict[languageEnum, CollectionGroupLocale]) -> list[CollectionGroupTranslation]:
        result = []
        for lang_key in languageEnum:
            locale = lang.get(lang_key)
            result.append(CollectionGroupTranslation(
                company_id=company_id,
                lang=lang_key.value,
                name=(locale.name if locale else None) or "",
                description=(locale.description if locale else None) or "",
            ))
        return result
