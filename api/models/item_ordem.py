from sqlalchemy import String, ForeignKey, text
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class ItemOrdem(Base):
    __tablename__ = "itens_ordem"

    id: Mapped[int] = mapped_column(NUMBER, primary_key=True, autoincrement=True)
    ordem_id: Mapped[int] = mapped_column(NUMBER, ForeignKey("ordens.id"), nullable=False)
    produto_id: Mapped[int] = mapped_column(NUMBER, ForeignKey("produtos.id"), nullable=False)
    endereco_id: Mapped[int] = mapped_column(NUMBER, ForeignKey("enderecos.id"), nullable=False)
    sequencia: Mapped[int] = mapped_column(NUMBER, nullable=False)
    qtd_solicitada: Mapped[int] = mapped_column(NUMBER, nullable=False)
    qtd_coletada: Mapped[int | None] = mapped_column(NUMBER, server_default=text("0"))
    status: Mapped[str] = mapped_column(String(20), server_default=text("'PENDENTE'"), nullable=False)

    ordem: Mapped["Ordem"] = relationship("Ordem", back_populates="itens")
    produto: Mapped["Produto"] = relationship("Produto", back_populates="itens_ordem")
    endereco: Mapped["Endereco"] = relationship("Endereco", back_populates="itens_ordem")
    logs: Mapped[list["LogColeta"]] = relationship("LogColeta", back_populates="item")
