import sqlalchemy as sa
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Ordem(Base):
    __tablename__ = "ordens"

    id: Mapped[int] = mapped_column(NUMBER, sa.Identity(start=1), primary_key=True)
    numero: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    operador_id: Mapped[int | None] = mapped_column(NUMBER, ForeignKey("operadores.id"))
    status: Mapped[str] = mapped_column(String(20), server_default=text("'AGUARDANDO'"), nullable=False)
    prioridade: Mapped[str] = mapped_column(String(10), server_default=text("'NORMAL'"), nullable=False)
    dt_criacao: Mapped[datetime] = mapped_column(DateTime, server_default=text("SYSDATE"), nullable=False)
    dt_inicio: Mapped[datetime | None] = mapped_column(DateTime)
    dt_conclusao: Mapped[datetime | None] = mapped_column(DateTime)

    operador: Mapped["Operador | None"] = relationship("Operador", back_populates="ordens")
    itens: Mapped[list["ItemOrdem"]] = relationship("ItemOrdem", back_populates="ordem")
