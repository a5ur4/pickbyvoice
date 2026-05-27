from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class LogColeta(Base):
    __tablename__ = "log_coleta"

    id: Mapped[int] = mapped_column(NUMBER, primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(NUMBER, ForeignKey("itens_ordem.id"), nullable=False)
    operador_id: Mapped[int] = mapped_column(NUMBER, ForeignKey("operadores.id"), nullable=False)
    codigo_informado: Mapped[str] = mapped_column(String(10), nullable=False)
    sucesso: Mapped[str] = mapped_column(String(1), nullable=False)
    tentativa: Mapped[int] = mapped_column(NUMBER, server_default=text("1"), nullable=False)
    dt_registro: Mapped[datetime] = mapped_column(DateTime, server_default=text("SYSDATE"), nullable=False)

    item: Mapped["ItemOrdem"] = relationship("ItemOrdem", back_populates="logs")
    operador: Mapped["Operador"] = relationship("Operador", back_populates="logs")
