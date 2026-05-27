from sqlalchemy import String, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(NUMBER, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    descricao: Mapped[str] = mapped_column(String(200), nullable=False)
    unidade: Mapped[str] = mapped_column(String(10), server_default=text("'UN'"), nullable=False)
    categoria: Mapped[str | None] = mapped_column(String(50))
    ativo: Mapped[str] = mapped_column(String(1), server_default=text("'S'"), nullable=False)

    estoques: Mapped[list["Estoque"]] = relationship("Estoque", back_populates="produto")
    itens_ordem: Mapped[list["ItemOrdem"]] = relationship("ItemOrdem", back_populates="produto")
