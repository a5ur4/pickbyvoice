from datetime import datetime
from sqlalchemy import String, DateTime, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Operador(Base):
    __tablename__ = "operadores"

    id: Mapped[int] = mapped_column(NUMBER, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    matricula: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(10), server_default=text("'ATIVO'"), nullable=False)
    dt_cadastro: Mapped[datetime] = mapped_column(DateTime, server_default=text("SYSDATE"), nullable=False)

    ordens: Mapped[list["Ordem"]] = relationship("Ordem", back_populates="operador")
    logs: Mapped[list["LogColeta"]] = relationship("LogColeta", back_populates="operador")
