from sqlalchemy import String, ForeignKey, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Endereco(Base):
    __tablename__ = "enderecos"

    id: Mapped[int] = mapped_column(NUMBER, primary_key=True, autoincrement=True)
    rua: Mapped[str] = mapped_column(String(5), nullable=False)
    coluna: Mapped[str] = mapped_column(String(5), nullable=False)
    nivel: Mapped[str] = mapped_column(String(5), nullable=False)
    apartamento: Mapped[str] = mapped_column(String(5), nullable=False)
    codigo_verificacao: Mapped[str] = mapped_column(String(10), nullable=False)
    setor_id: Mapped[int] = mapped_column(NUMBER, ForeignKey("setores.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(10), server_default=text("'ATIVO'"), nullable=False)

    setor: Mapped["Setor"] = relationship("Setor", back_populates="enderecos")
    estoques: Mapped[list["Estoque"]] = relationship("Estoque", back_populates="endereco")
    itens_ordem: Mapped[list["ItemOrdem"]] = relationship("ItemOrdem", back_populates="endereco")
