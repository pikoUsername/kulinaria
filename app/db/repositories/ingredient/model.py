from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa

from app.db.repositories.base import TimedModel


class Ingredient(TimedModel):
    """
    Will be connected directly to recipe, without any middle tables
    """
    __tablename__ = "ingredients"

    name: Mapped[str] = mapped_column(sa.String(52))
    price: Mapped[float] = mapped_column()  # price for 1 kg
    mass: Mapped[Optional[int]] = mapped_column()  # in gramms
