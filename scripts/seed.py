"""Тестовые данные для среза модуля групп коллекций
Идемпотентен: повторный запуск ничего не делает, --reset чистит и создаёт заново
Запуск: groups/bin/python scripts/seed.py --reset
"""

import argparse
import asyncio
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1] / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

import db.session as _db_session
from db.models.models import (
    CollectionGroup,
    CollectionGroupTranslation,
    CollectionRealm,
    Company,
)


def session_factory():
    """Ищет async_sessionmaker в db.session по типу — имя не важно."""
    for name, value in vars(_db_session).items():
        if name.startswith("_"):
            continue
        if isinstance(value, async_sessionmaker):
            print(f"фабрика сессий: db.session.{name}")
            return value

    names = [n for n in dir(_db_session) if not n.startswith("_")]
    raise SystemExit("в db.session нет async_sessionmaker. Что есть: " + ", ".join(names))


async def _wipe(session) -> None:
    await session.execute(delete(CollectionRealm))
    await session.execute(delete(CollectionGroupTranslation))
    await session.execute(delete(CollectionGroup))
    await session.execute(delete(Company))
    await session.commit()


def _make_group(
    session,
    company: Company,
    *,
    order: int,
    image: str | None = None,
    disable: bool = False,
    archived: bool = False,
    translations: tuple[tuple[str, str | None, str | None], ...] = (),
) -> CollectionGroup:
    group = CollectionGroup(
        company_id=company.id,
        order=order,
        image=image,
        disable=disable,
        archived=archived,
    )
    session.add(group)
    for lang, name, description in translations:
        # append в relationship: relation_id SQLAlchemy проставит сам на flush
        group.translations.append(
            CollectionGroupTranslation(
                company_id=company.id,
                lang=lang,
                name=name,
                description=description,
            )
        )
    return group


async def seed(reset: bool) -> None:
    maker = session_factory()
    async with maker() as session:
        if reset:
            await _wipe(session)
            print("таблицы очищены")

        if await session.scalar(select(func.count()).select_from(Company)):
            print("данные уже есть — пропускаю (--reset чтобы пересоздать)")
            return

        demo = Company(name="Demo Retail")
        second = Company(name="Second Brand")
        session.add_all([demo, second])
        await session.flush()

        summer = _make_group(
            session, demo,
            order=1,
            image="/media/collection_group/summer.jpg",
            translations=(
                ("ru", "Летняя коллекция", "Подборка для летнего сезона"),
                ("en", "Summer collection", "Summer season picks"),
            ),
        )
        winter = _make_group(
            session, demo,
            order=2,
            disable=True,
            translations=(("ru", "Зимняя коллекция", None),),
        )
        draft = _make_group(session, demo, order=3, archived=True)
        other = _make_group(
            session, second,
            order=1,
            translations=(
                ("ru", "Чужая компания", None),
                ("en", "Another company", None),
            ),
        )
        await session.flush()

        realms = [
            CollectionRealm(group_id=summer.id, company_id=demo.id, order=1),
            CollectionRealm(group_id=summer.id, company_id=demo.id, order=2),
            CollectionRealm(group_id=summer.id, company_id=demo.id, order=3),
            CollectionRealm(group_id=winter.id, company_id=demo.id, order=1),
            CollectionRealm(group_id=winter.id, company_id=demo.id, order=2),
            CollectionRealm(group_id=None, company_id=demo.id, order=4),
            CollectionRealm(group_id=None, company_id=demo.id, order=5),
            CollectionRealm(group_id=other.id, company_id=second.id, order=1),
            CollectionRealm(group_id=other.id, company_id=second.id, order=2),
        ]
        session.add_all(realms)
        await session.flush()

        print(f"company          : {demo.id} {demo.name} / {second.id} {second.name}")
        print(f"collection_group : 4")
        print(f"  id={summer.id} order=1 ru+en realms=3  Летняя коллекция")
        print(f"  id={winter.id} order=2 ru    realms=2  disable=True")
        print(f"  id={draft.id} order=3 —     realms=0  archived=True")
        print(f"  id={other.id} order=1 ru+en realms=2  company={second.id}")
        print(f"collection_realm : {len(realms)}")
        print(f"translation      : 5")

        await session.commit()
        print("готово")


def main() -> None:
    parser = argparse.ArgumentParser(description="Тестовые данные среза")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    asyncio.run(seed(reset=args.reset))


if __name__ == "__main__":
    main()
