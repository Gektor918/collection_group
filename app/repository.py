from dataclasses import dataclass

from sqlalchemy import case, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.models import (CollectionGroup, CollectionGroupTranslation,
                            CollectionRealm)


@dataclass(frozen=True)
class GroupUpdateResult:
    group: CollectionGroup
    old_image: str | None


@dataclass(frozen=True)
class GroupDeleteResult:
    group_id: int
    old_image: str | None


class CollectionGroupRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        group_id: int,
        company_id: int,
    ) -> CollectionGroup | None:

        stmt = select(CollectionGroup).where(
            CollectionGroup.id == group_id,
            CollectionGroup.company_id == company_id,
        )
        return await self.session.scalar(stmt)

    async def list_by_company(
        self,
        company_id: int,
    ) -> list[CollectionGroup]:
        stmt = (
            select(CollectionGroup)
            .where(CollectionGroup.company_id == company_id)
            .options(selectinload(CollectionGroup.translations))
            .order_by(
                CollectionGroup.order.asc().nulls_last(),
                CollectionGroup.id.asc(),
            )
        )
        return list((await self.session.scalars(stmt)).all())

    async def create_group(
        self,
        company_id: int,
        translations: list[CollectionGroupTranslation],
        image: str | None = None,
    ) -> CollectionGroup:
        group = CollectionGroup(company_id=company_id, image=image)
        group.translations.extend(translations)
        self.session.add(group)
        await self.session.flush()
        group.order = group.id
        return group

    async def update_group(
        self,
        group_id: int,
        company_id: int,
        lang: dict| None = None,
        image: str | None = None,
        disable: bool | None = None,
    ) -> GroupUpdateResult | None:
        stmt = (
            select(CollectionGroup)
            .where(
                CollectionGroup.id == group_id,
                CollectionGroup.company_id == company_id,
            )
            .options(selectinload(CollectionGroup.translations))
        )
        group = await self.session.scalar(stmt)
        if group is None:
            return None

        old_image = group.image

        if image is not None:
            group.image = image
        if disable is not None:
            group.disable = disable

        if lang is not None:
            existing_by_lang = {t.lang: t for t in group.translations}

            for lang_key, locale in lang.items():
                existing = existing_by_lang.get(lang_key.value)
                if existing is None:
                    new_translation = CollectionGroupTranslation(
                        company_id=company_id,
                        lang=lang_key.value,
                        name=locale.name or "",
                        description=locale.description or "",
                    )
                    group.translations.append(new_translation)
                    continue

                if locale.name is not None:
                    existing.name = locale.name
                if locale.description is not None:
                    existing.description = locale.description
        return GroupUpdateResult(group=group, old_image=old_image)

    async def delete_group(
        self,
        group_id: int,
        company_id: int,
    ) -> GroupDeleteResult | None:
        stmt = (
            select(CollectionGroup)
            .where(
                CollectionGroup.id == group_id,
                CollectionGroup.company_id == company_id,
            )
            .options(selectinload(CollectionGroup.translations))
        )
        group = await self.session.scalar(stmt)
        if group is None:
            return None
        old_image = group.image
        del_id = group.id
        await self.session.delete(group)
        return GroupDeleteResult(group_id=del_id, old_image=old_image)

    async def assign_collections_to_group(
        self,
        group_id: int,
        company_id: int,
        collection_ids: list[int],
    ) -> list[int]:
        if not collection_ids:
            return []
        stmt = (
            update(CollectionRealm)
            .where(
                CollectionRealm.id.in_(collection_ids),
                CollectionRealm.company_id == company_id,
            )
            .values(group_id=group_id)
            .returning(CollectionRealm.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def unassign_collections_from_group(
        self,
        group_id: int,
        company_id: int,
        collection_ids: list[int],
    ) -> list[int]:
        if not collection_ids:
            return []
        stmt = (
            update(CollectionRealm)
            .where(
                CollectionRealm.id.in_(collection_ids),
                CollectionRealm.company_id == company_id,
                CollectionRealm.group_id == group_id,
            )
            .values(group_id=None)
            .returning(CollectionRealm.id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_order(
        self,
        company_id: int,
        orders: dict[int, int],
    ) -> dict[int, int]:
        if not orders:
            return {}
        case_stmt = case(
            *((CollectionGroup.id == gid, order) for gid, order in orders.items()),
            else_=CollectionGroup.order
        )
        stmt = (
            update(CollectionGroup)
            .where(
                CollectionGroup.id.in_(orders.keys()),
                CollectionGroup.company_id == company_id,
            )
            .values(order=case_stmt)
            .returning(CollectionGroup.id, CollectionGroup.order)
        )
        result = await self.session.execute(stmt)
        return {group_id: new_order for group_id, new_order in result}

    async def count_realms(self, company_id: int) -> tuple[int, int, int]:
        row = (await self.session.execute(
            select(
                func.count().label("total"),
                func.count().filter(CollectionRealm.group_id.is_not(None)).label("assigned"),
            ).where(CollectionRealm.company_id == company_id)
        )).one()
        total, assigned = row.total or 0, row.assigned or 0
        return total, assigned, total - assigned

    async def list_realms(
        self,
        company_id: int,
        *,
        group_id: int | None = None,
        assigned: bool | None = None,
    ) -> list[CollectionRealm]:
        stmt = select(CollectionRealm).where(CollectionRealm.company_id == company_id)

        if group_id is not None:
            stmt = stmt.where(CollectionRealm.group_id == group_id)
        if assigned is True:
            stmt = stmt.where(CollectionRealm.group_id.is_not(None))
        elif assigned is False:
            stmt = stmt.where(CollectionRealm.group_id.is_(None))

        stmt = stmt.order_by(
            CollectionRealm.group_id.nulls_last(),
            CollectionRealm.order.nulls_last(),
            CollectionRealm.id,
        )
        return list((await self.session.scalars(stmt)).all())
