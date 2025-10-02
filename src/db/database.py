from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, class_mapper
from sqlalchemy import Integer, func, Text, ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncAttrs

phone_number = Annotated[str, mapped_column(String(20), index=True)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"
