from sqlalchemy import Boolean, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))


class CollectionGroup(Base):
    __tablename__ = "collection_group"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("company.id"), index=True
    )
    image: Mapped[str | None] = mapped_column(String(256))
    order: Mapped[int | None] = mapped_column(Integer)
    disable: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    archived: Mapped[bool | None] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )

    translations: Mapped[list["CollectionGroupTranslation"]] = relationship(
        "CollectionGroupTranslation",
        back_populates="collection_group",
        cascade="all, delete-orphan",
    )
    collections: Mapped[list["CollectionRealm"]] = relationship(
        "CollectionRealm",
        back_populates="group",
    )

    def as_dict(self):
        return dict(
            id=self.id,
            image=self.image,
            disable=self.disable,
            order=self.order,
        )


class CollectionGroupTranslation(Base):
    __tablename__ = "collection_group_translation"

    id: Mapped[int] = mapped_column(primary_key=True)
    relation_id: Mapped[int] = mapped_column(ForeignKey("collection_group.id"))
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("company.id"), index=True
    )
    lang: Mapped[str] = mapped_column(String(2), nullable=False)
    name: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(512))

    collection_group: Mapped["CollectionGroup"] = relationship(
        back_populates="translations"
    )

    def as_dict_translation(self):
        return dict(lang=self.lang, name=self.name)


class CollectionRealm(Base):
    __tablename__ = "collection_realm"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("collection_group.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        default=None,
    )
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("company.id"), index=True
    )
    order: Mapped[int | None] = mapped_column(Integer)

    group: Mapped["CollectionGroup | None"] = relationship(
        "CollectionGroup",
        back_populates="collections",
    )
