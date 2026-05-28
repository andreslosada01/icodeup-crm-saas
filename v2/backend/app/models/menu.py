from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class MenuItem(Base):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    route_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    url: Mapped[str | None] = mapped_column(String(240))
    icon: Mapped[str | None] = mapped_column(String(80))
    module_id: Mapped[int | None] = mapped_column(ForeignKey("modules.id"), index=True)
    module_code: Mapped[str | None] = mapped_column(String(80), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("menu_items.id"), index=True)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    required_permission: Mapped[str | None] = mapped_column(String(120), index=True)
    required_permission_code: Mapped[str | None] = mapped_column(String(120), index=True)
    audience: Mapped[str] = mapped_column(String(40), default="operational_user", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    module = relationship("Module")
    parent = relationship("MenuItem", remote_side=[id])
