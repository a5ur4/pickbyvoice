import sqlalchemy as sa
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Estoque(Base):
    __tablename__ = "estoque"

    id: Mapped[int] = mapped_column(NUMBER, sa.Identity(start=1), primary_key=True)
    produto_id: Mapped[int] = mapped_column(NUMBER, ForeignKey("produtos.id"), nullable=False)
    endereco_id: Mapped[int] = mapped_column(NUMBER, ForeignKey("enderecos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(NUMBER, server_default=text("0"), nullable=False)
    dt_atualizacao: Mapped[datetime] = mapped_column(DateTime, server_default=text("SYSDATE"), nullable=False)

    produto: Mapped["Produto"] = relationship("Produto", back_populates="estoques")
    endereco: Mapped["Endereco"] = relationship("Endereco", back_populates="estoques")
